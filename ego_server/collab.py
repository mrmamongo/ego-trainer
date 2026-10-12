"""Collaborative editing backend (ADR-0017, P1 MVP): Yjs rooms over WebSocket.

- Transport: ``ypy-websocket`` mounted as a raw ASGI sub-app at
  ``/collab/ws/{room}`` inside the main uvicorn process — no extra Node
  service, no extra container (ADR-0017 D17.1/D17.4).
- Rooms: ``scenario:taskId:fileKey`` with a per-scenario ACL (D17.3):
  ``studio`` → mentor/admin, ``defense`` and ``pair`` → any authenticated
  user (P1).
- Persistence: rooms live in process memory; the Y-state is snapshotted into
  the ``collab_snapshots`` SQLite table whenever a room is dropped (last
  client left, idle sweep, server shutdown), and a fresh room is hydrated
  from that snapshot (D17.5).
- Коммит в канонический контент по-прежнему идёт через Task Studio;
  коллаб-документ — черновик (D17.2).
"""

from __future__ import annotations

import asyncio
import contextlib
import gc
import logging
import re
import secrets
import sqlite3
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import NamedTuple
from urllib.parse import parse_qs

import y_py as Y
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from pydantic import BaseModel
from starlette.responses import PlainTextResponse
from starlette.types import Receive, Scope, Send
from ypy_websocket import WebsocketServer, YRoom
from ypy_websocket.asgi_server import ASGIServer

from ego_server import config, db
from ego_server.auth import decode_token
from ego_server.deps import CurrentUser, require_role

log = logging.getLogger(__name__)

# === Грамматика имени комнаты и ACL (ADR-0017 D17.3) ===

_SCENARIOS = ("studio", "defense", "pair", "share")
_STUDIO_FILE_KEYS = ("markdown", "solution_py", "tests_py")
_FREE_FILE_KEY_RE = re.compile(r"[A-Za-z0-9_-]{1,64}")
_TASK_ID_RE = re.compile(r"[A-Za-z0-9._-]{1,64}")
_SHARE_ROOM_ID_RE = re.compile(r"[A-Za-z0-9_-]{16,64}")

# Минимальный «пустой» update от y_py (см. ypy-websocket/yutils.py, y-py #98).
_EMPTY_UPDATE = b"\x00\x00"


class RoomSpec(NamedTuple):
    """Разобранное имя комнаты ``scenario:taskId:fileKey``."""

    scenario: str
    task_id: str
    file_key: str


def parse_room(name: str) -> RoomSpec:
    """Разобрать и провалидировать имя комнаты; ValueError если оно кривое.

    Грамматика: ``scenario:taskId:fileKey``, где scenario —
    studio|defense|pair|share. Для studio/defense/pair taskId — это id задачи
    (``[A-Za-z0-9._-]{1,64}``, существование в БД проверяется отдельно в
    ``_task_exists``); для share «taskId»-слот занимает непрозрачный id
    share-комнаты (``[A-Za-z0-9_-]{16,64}``, существование/active — в
    ``_share_room_row``). fileKey — markdown|solution_py|tests_py для studio
    и ``[A-Za-z0-9_-]{1,64}`` для остальных сценариев.
    """
    parts = name.split(":")
    if len(parts) != 3:
        raise ValueError(f"Malformed room name: {name!r}")
    scenario, task_id, file_key = parts
    if scenario not in _SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario!r}")
    if scenario == "share":
        if not _SHARE_ROOM_ID_RE.fullmatch(task_id):
            raise ValueError(f"Malformed share room id: {task_id!r}")
    elif not _TASK_ID_RE.fullmatch(task_id):
        raise ValueError(f"Malformed task id in room: {task_id!r}")
    if scenario == "studio":
        if file_key not in _STUDIO_FILE_KEYS:
            raise ValueError(f"Bad studio file key: {file_key!r}")
    elif not _FREE_FILE_KEY_RE.fullmatch(file_key):
        raise ValueError(f"Bad file key: {file_key!r}")
    return RoomSpec(scenario=scenario, task_id=task_id, file_key=file_key)


def room_allowed(user: dict, spec: RoomSpec) -> bool:
    """Scenario ACL. ``user`` — свежие из БД клеймы (см. ``_ws_user``).

    share-комнаты дополнительно проверяются на active в ``_handshake_allowed``:
    ссылка = capability, доступа «по списку задач» нет.
    """
    role = user.get("role", "")
    if spec.scenario == "studio":
        return role in ("mentor", "admin")
    # defense / pair / share: любой аутентифицированный пользователь,
    # у share — при наличии валидной активной комнаты (проверяется отдельно).
    return True


# === Auth для ws-хендшейка ===


def _ws_user(token: str | None) -> dict | None:
    """Проверить JWT и вернуть свежие из БД клеймы пользователя, либо None.

    Повторяет логику ``ego_server.deps.get_current_user``, но с коротким
    sqlite-соединением: у сырого ASGI-хендшейка нет FastAPI-зависимостей.
    """
    if not token:
        return None
    try:
        claims = decode_token(token)
    except Exception:  # noqa: BLE001 — любая ошибка токена = отказ
        return None
    try:
        conn = db.get_connection()
    except Exception:  # noqa: BLE001 — БД недоступна
        return None
    try:
        row = conn.execute(
            "SELECT id, username, role FROM students WHERE id=?", (claims.get("sub"),)
        ).fetchone()
    except Exception:  # noqa: BLE001
        return None
    finally:
        conn.close()
    if row is None:
        return None
    # Привилегии берём из текущего состояния БД, а не из клеймов JWT.
    return {**claims, "username": row["username"], "role": row["role"]}


def _task_exists(task_id: str) -> bool:
    """Существует ли задача с таким id в таблице tasks."""
    try:
        conn = db.get_connection()
    except Exception:  # noqa: BLE001
        return False
    try:
        return (
            conn.execute("SELECT 1 FROM tasks WHERE id=? LIMIT 1", (task_id,)).fetchone()
            is not None
        )
    except Exception:  # noqa: BLE001
        return False
    finally:
        conn.close()


def share_room_row(room_id: str) -> sqlite3.Row | None:
    """Активная share-комната по её непрозрачному id (или None)."""
    conn = db.get_connection()
    try:
        return conn.execute(
            "SELECT id, task_id, title, created_by, active FROM collab_share_rooms "
            "WHERE id=? AND active=1 LIMIT 1",
            (room_id,),
        ).fetchone()
    finally:
        conn.close()


def _token_from_scope(scope: dict) -> str | None:
    """JWT из query-параметра ``token``."""
    query = scope.get("query_string") or b""
    params = parse_qs(query.decode("utf-8", "replace"))
    values = params.get("token")
    return values[0] if values else None


def _room_from_scope(scope: dict) -> str | None:
    """Голое имя комнаты из path смонтированного scope.

    Внутри mount starlette оставляет в ``scope['path']`` ПОЛНЫЙ путь, а префикс
    кладёт в ``scope['root_path']``; поддерживаем обе формы —
    ``/collab/ws/<room>`` и ``/<room>``.
    """
    path = scope.get("path") or ""
    root = scope.get("root_path") or ""
    if root and path.startswith(root):
        path = path[len(root) :]
    if path.startswith("/collab/ws"):
        path = path[len("/collab/ws") :]
    path = path.strip("/")
    return path or None


# === Снапшоты (SQLite, ADR-0017 D17.5) ===


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _save_snapshot(room_name: str, ydoc: Y.YDoc) -> None:
    """Upsert Y-state и плоского текста комнаты в ``collab_snapshots``."""
    ystate = bytes(Y.encode_state_as_update(ydoc))
    text = str(ydoc.get_text("content"))
    conn = db.get_connection()
    try:
        conn.execute(
            """
            INSERT INTO collab_snapshots (room, ystate, text, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(room) DO UPDATE SET
              ystate=excluded.ystate,
              text=excluded.text,
              updated_at=excluded.updated_at
            """,
            (room_name, ystate, text, _now_iso()),
        )
        conn.commit()
    finally:
        conn.close()


def _load_snapshot(room_name: str) -> tuple[bytes, str, str] | None:
    """``(ystate, text, updated_at)`` для комнаты, либо None."""
    conn = db.get_connection()
    try:
        row = conn.execute(
            "SELECT ystate, text, updated_at FROM collab_snapshots WHERE room=?",
            (room_name,),
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        return None
    return bytes(row["ystate"]), str(row["text"]), str(row["updated_at"])


def _doc_from_text(content: str) -> Y.YDoc:
    """Свежий YDoc, чей текст 'content' равен ``content``."""
    ydoc = Y.YDoc()
    if content:
        ytext = ydoc.get_text("content")
        with ydoc.begin_transaction() as tx:
            ytext.insert(tx, 0, content)
    return ydoc


# === Сервер комнат: гидратация при открытии, снапшот при закрытии ===


class CollabWebsocketServer(WebsocketServer):
    """``WebsocketServer``, политый свежие комнаты из collab_snapshots.

    ypy-websocket с ``auto_clean_rooms=True`` сам удаляет комнату, когда ушёл
    последний клиент (``_serve``), поэтому снапшот пишется в переопределённом
    ``delete_room`` — иначе текст, написанный за <30с до дисконнекта,
    терялся бы до тика sweeper'а.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]
        # Имена комнат, уже политых из снапшота.
        self._hydrated: set[str] = set()

    async def get_room(self, name: str) -> YRoom:
        room = await super().get_room(name)
        if name not in self._hydrated:
            self._hydrated.add(name)
            try:
                snapshot = _load_snapshot(name)
            except Exception:  # noqa: BLE001
                log.exception("collab: не удалось прочитать снапшот %s", name)
                snapshot = None
            if snapshot is not None:
                ystate = snapshot[0]
                if ystate and ystate != _EMPTY_UPDATE:
                    Y.apply_update(room.ydoc, ystate)
                    log.info("collab: комната %s политa из снапшота", name)
        return room

    def delete_room(self, *, name: str | None = None, room: YRoom | None = None) -> None:
        """Сохранить снапшот и убрать комнату из реестра (любой путь вызова).

        В отличие от ``WebsocketServer.delete_room`` мы НЕ вызываем
        ``room.stop()``: он выставляет ``room._task_group = None``, а
        ``_broadcast_updates`` (задача того же task group'а) после этого
        падает с AttributeError на ``cancel_scope`` — гонка внутри
        ypy-websocket 0.12.4. Task group комнаты будет отменён вызывающей
        стороной (``_serve`` отменяет свой scope сразу после автоочистки).
        """
        if name is not None and room is not None:
            raise RuntimeError("Cannot pass name and room")
        target = name
        if target is None:
            if room is None:
                raise RuntimeError("Either name or room must be passed")
            try:
                target = self.get_room_name(room)
            except ValueError:
                # Комнату уже удалили другим путём (например, reset-эндпоинт) —
                # повторная автоочистка _serve не должна ронять serve-таску.
                return
        live = self.rooms.pop(target, None)
        self._hydrated.discard(target)
        if live is not None:
            try:
                _save_snapshot(target, live.ydoc)
            except Exception:  # noqa: BLE001 — снапшот best-effort
                log.exception("collab: снапшот при удалении %s не записан", target)


class CollabServer:
    """Владеет жизненным циклом ws-сервера и задачей снапшот-свипера."""

    def __init__(self) -> None:
        self.ws = CollabWebsocketServer(rooms_ready=True, auto_clean_rooms=True, log=log)
        self._sweeper: asyncio.Task[None] | None = None

    @asynccontextmanager
    async def start(self):
        """Запустить ws-сервер + свипер на время жизни приложения."""
        try:
            async with self.ws:
                self._sweeper = asyncio.create_task(self._sweep_idle_rooms())
                try:
                    yield
                finally:
                    self._sweeper.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await self._sweeper
                    self._sweeper = None
                    # Сохраняем все живые комнаты перед остановкой процесса.
                    for room_name, room in list(self.ws.rooms.items()):
                        try:
                            _save_snapshot(room_name, room.ydoc)
                        except Exception:  # noqa: BLE001
                            log.exception("collab: shutdown-снапшот %s не записан", room_name)
                    # Чистим словарь в потоке event-loop: YDoc прибивается в своём потоке.
                    self.ws.rooms.clear()
        finally:
            # YRoom/YDoc содержат циклы ссылок; без явного gc.collect() их
            # финализаторы позже пойдут в произвольном потоке (например, в
            # pytest), и y_py падает «YDoc is unsendable, but is dropped on
            # another thread». Собираем циклы здесь, в потоке event-loop'а,
            # уже после разматывания task group'ов ws-сервера.
            gc.collect()

    async def _sweep_idle_rooms(self) -> None:
        """Раз в интервал: активные комнаты снапшотим, пустые — выгружаем."""
        interval = max(1.0, float(config.settings.collab_snapshot_interval_seconds))
        while True:
            await asyncio.sleep(interval)
            for room_name, room in list(self.ws.rooms.items()):
                try:
                    if room.clients:
                        _save_snapshot(room_name, room.ydoc)
                    else:
                        self.ws.delete_room(name=room_name)  # снапшот внутри
                except Exception:  # noqa: BLE001
                    log.exception("collab: idle-sweep не обработал %s", room_name)


# === ASGI-обвязка: auth + ACL на ws-хендшейке ===

_WS_MOUNT = "/collab/ws"


class CollabWSApp:
    """ASGI-гейт: JWT-auth + ACL комнаты, затем ypy-websocket-сервер.

    Решение принимается в ``ASGIServer.on_connect`` (True = «не принято»).
    Обычный on_connect-отказ просто возвращается без accept/close — реальный
    сервер закрывает соединение на транспортном уровне, но starlette TestClient
    ждал бы вечно, поэтому после отклонённого хендшейка дополнительно
    отправляется явный ``websocket.close``.
    """

    def __init__(self, ws_server: CollabWebsocketServer) -> None:
        self._ws_server = ws_server

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "websocket":
            await PlainTextResponse("collab: websocket endpoint", status_code=404)(
                scope, receive, send
            )
            return
        room = _room_from_scope(scope)  # type: ignore[arg-type]
        # Ключ комнаты в WebsocketServer = websocket.path = голое имя комнаты,
        # чтобы ключи совпадали с именами снапшотов и REST-эндпоинтов.
        inner_scope = {**scope, "path": room or ""}
        accepted = False

        async def _send(message: dict) -> None:
            nonlocal accepted
            if message.get("type") == "websocket.accept":
                accepted = True
            await send(message)  # type: ignore[arg-type]

        async def _on_connect(msg: dict, inner: dict) -> bool:
            # True = отклонить (контракт ASGIServer.on_connect).
            return not self._handshake_allowed(inner, room)

        await ASGIServer(self._ws_server, on_connect=_on_connect)(
            inner_scope,
            receive,
            _send,  # type: ignore[arg-type]
        )
        if not accepted:
            await send(  # type: ignore[func-returns-value]
                {"type": "websocket.close", "code": 1008, "reason": "collab: rejected"}
            )

    def _handshake_allowed(self, scope: dict, room: str | None) -> bool:
        """Authn + грамматика комнаты + задача/ share-комната + scenario ACL."""
        if not room:
            log.warning("collab ws: отказ (нет комнаты в path)")
            return False
        user = _ws_user(_token_from_scope(scope))
        if user is None:
            log.warning("collab ws: отказ (auth) room=%s", room)
            return False
        try:
            spec = parse_room(room)
        except ValueError:
            log.warning("collab ws: отказ (имя комнаты) %r", room)
            return False
        if spec.scenario == "share":
            # Ссылка = capability: имя комнаты угадать нельзя, список комнат
            # не отдаётся; вход только с валидным активным id.
            if share_room_row(spec.task_id) is None:
                log.info("collab ws: отказ (share-комната закрыта/не найдена) %s", spec.task_id)
                return False
        elif not _task_exists(spec.task_id):
            log.warning("collab ws: отказ (нет задачи) %r", spec.task_id)
            return False
        if not room_allowed(user, spec):
            log.info(
                "collab ws: отказ (acl) room=%s user=%s role=%s",
                room,
                user.get("username"),
                user.get("role"),
            )
            return False
        return True


# === REST-эндпоинты ===


class CollabResetRequest(BaseModel):
    content: str


class ShareRoomCreateRequest(BaseModel):
    task_id: str
    title: str = ""


def create_collab_router() -> APIRouter:
    """Роутер коллаба: чтение снапшота и сброс комнаты."""
    router = APIRouter()

    @router.get("/collab/rooms/{room}/snapshot")
    async def room_snapshot(room: str, user: CurrentUser) -> dict:
        """Текущий текст комнаты: живая in-memory, иначе снапшот из SQLite."""
        try:
            spec = parse_room(room)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        # ACL как у ws: studio-файлы скрывают решение от студентов.
        if not room_allowed(user, spec):
            raise HTTPException(status_code=403, detail="No access to this room")
        live = get_collab_server().ws.rooms.get(room)
        if live is not None:
            return {
                "room": room,
                "text": str(live.ydoc.get_text("content")),
                "updated_at": _now_iso(),
            }
        snapshot = _load_snapshot(room)
        if snapshot is None:
            raise HTTPException(status_code=404, detail="No snapshot for this room yet")
        _ystate, text, updated_at = snapshot
        return {"room": room, "text": text, "updated_at": updated_at}

    @router.post(
        "/collab/rooms/{room}/reset",
        dependencies=[Depends(require_role("mentor", "admin"))],
    )
    async def room_reset(room: str, body: CollabResetRequest) -> dict:
        """Сбросить комнату в ``content``: остановить живую, записать свежий YDoc."""
        try:
            parse_room(room)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        if len(body.content.encode("utf-8")) > config.settings.collab_max_room_text_bytes:
            raise HTTPException(
                status_code=413,
                detail="Content exceeds the collab room size limit",
            )
        collab = get_collab_server()
        if room in collab.ws.rooms:
            try:
                collab.ws.delete_room(name=room)  # снапшот + снятие гидратации
            except Exception:  # noqa: BLE001
                log.exception("collab: reset не остановил живую комнату %s", room)
        try:
            _save_snapshot(room, _doc_from_text(body.content))
        except Exception as e:  # noqa: BLE001
            raise HTTPException(status_code=500, detail=f"Snapshot write failed: {e}") from e
        return {"ok": True}

    # --- Share-комнаты: вход по непрозрачной ссылке (D17.3, M2-подготовка) ---

    @router.post("/collab/share", dependencies=[Depends(require_role("mentor", "admin"))])
    async def share_room_create(body: ShareRoomCreateRequest, user: CurrentUser) -> dict:
        """Создать share-комнату для задачи и вернуть её ссылку-capability.

        Id непрозрачен (secrets.token_urlsafe(12)), списка комнат нет —
        подключиться можно только по ссылке ``/ide/room/<id>``.
        """
        task_id = body.task_id.strip()
        if not _task_exists(task_id):
            raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
        room_id = secrets.token_urlsafe(12)  # ~16 chars, unguessable
        conn = db.get_connection()
        try:
            conn.execute(
                "INSERT INTO collab_share_rooms (id, task_id, title, created_by, "
                "active, created_at) VALUES (?, ?, ?, ?, 1, ?)",
                (room_id, task_id, body.title.strip()[:120], user["sub"], _now_iso()),
            )
            conn.commit()
        finally:
            conn.close()
        log.info("collab share: создана комната %s (task=%s, by=%s)", room_id, task_id, user["sub"])
        return {"room_id": room_id, "task_id": task_id, "title": body.title.strip()[:120], "active": True}

    @router.get("/collab/share/{room_id}")
    async def share_room_get(room_id: str, user: CurrentUser) -> dict:
        """Метаданные активной share-комнаты (проверка ссылки перед входом)."""
        row = share_room_row(room_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Share room not found or closed")
        return {
            "room_id": row["id"],
            "task_id": row["task_id"],
            "title": row["title"],
            "created_by": row["created_by"],
            "active": bool(row["active"]),
        }

    @router.post("/collab/share/{room_id}/close")
    async def share_room_close(room_id: str, user: CurrentUser) -> dict:
        """Закрыть комнату: создатель или admin. Новые ws-коннекты отклоняются."""
        conn = db.get_connection()
        try:
            row = conn.execute(
                "SELECT id, created_by, active FROM collab_share_rooms WHERE id=? LIMIT 1",
                (room_id,),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            raise HTTPException(status_code=404, detail="Share room not found")
        if user["role"] != "admin" and user["sub"] != row["created_by"]:
            raise HTTPException(status_code=403, detail="Only the creator or an admin can close")
        if row["active"]:
            conn = db.get_connection()
            try:
                conn.execute(
                    "UPDATE collab_share_rooms SET active=0, closed_at=? WHERE id=?",
                    (_now_iso(), room_id),
                )
                conn.commit()
            finally:
                conn.close()
        log.info("collab share: комната %s закрыта (by=%s)", room_id, user["sub"])
        return {"ok": True, "room_id": room_id, "active": False}

    return router


# === Подключение к приложению ===


def mount_collab(app: FastAPI) -> None:
    """Зарегистрировать REST-роутер и смонтировать ws ASGI sub-app."""
    app.include_router(create_collab_router(), tags=["collab"])
    app.mount(_WS_MOUNT, CollabWSApp(get_collab_server().ws), name="collab-ws")


_collab_server: CollabServer | None = None


def get_collab_server() -> CollabServer:
    """Синглтон уровня модуля: комнаты живут в памяти процесса."""
    global _collab_server
    if _collab_server is None:
        _collab_server = CollabServer()
    return _collab_server
