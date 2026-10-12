"""Collaborative editing server (ADR-0017): Yjs rooms over WebSocket.

Design (ADR-0017 D17.1-D17.5):
- Transport: ypy-websocket ``WebsocketServer`` mounted as an ASGI sub-app at
  ``/collab/ws/{room}`` inside the main uvicorn process — no extra Node
  service, no extra container.
- Rooms: ``scenario:taskId:fileKey`` with per-scenario ACL
  (studio → mentor/admin; defense → any authenticated user; pair → any
  authenticated user for P1).
- Persistence: in-memory rooms + idle snapshots into ``collab_snapshots``
  (SQLite). A fresh room is hydrated from its snapshot, so a reopened
  document continues where the last session left off.
- Commit to canonical content still flows through Task Studio
  (``PUT /admin/tasks/{id}/studio``) — the collab doc is a draft layer.
"""

from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime, timezone
from typing import Any

import y_py as Y
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from ego_server.auth import decode_token
from ego_server.config import settings
from ego_server.db import get_connection
from ego_server.deps import CurrentUser, require_role

log = logging.getLogger(__name__)

# === Room grammar and ACL (ADR-0017 D17.3) ===

_SCENARIOS = ("studio", "defense", "pair")
_STUDIO_FILES = ("markdown", "solution_py", "tests_py")
_FREE_FILE_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
_TASK_ID_RE = re.compile(r"^[^:/\\]{1,128}$")


class RoomSpec(BaseModel):
    scenario: str
    task_id: str
    file_key: str


def parse_room(name: str) -> RoomSpec:
    """Parse ``scenario:taskId:fileKey``; ValueError on malformed input."""
    parts = name.split(":")
    if len(parts) != 3:
        raise ValueError(f"Malformed room name: {name!r}")
    scenario, task_id, file_key = parts
    if scenario not in _SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario!r}")
    if not _TASK_ID_RE.fullmatch(task_id):
        raise ValueError(f"Malformed task id in room: {task_id!r}")
    if scenario == "studio":
        if file_key not in _STUDIO_FILES:
            raise ValueError(f"Bad studio file key: {file_key!r}")
    elif not _FREE_FILE_RE.fullmatch(file_key):
        raise ValueError(f"Bad file key: {file_key!r}")
    return RoomSpec(scenario=scenario, task_id=task_id, file_key=file_key)


def room_allowed(user: dict, spec: RoomSpec) -> bool:
    """Scenario ACL. ``user`` is the DB-fresh claims dict from _ws_user."""
    role = user.get("role", "student")
    if spec.scenario == "studio":
        return role in ("mentor", "admin")
    # defense / pair: any authenticated user in P1.
    return True


def _ws_user(token: str | None) -> dict | None:
    """Verify a JWT and return DB-fresh user claims, or None."""
    if not token:
        return None
    try:
        claims = decode_token(token)
    except Exception:  # noqa: BLE001 — any token error rejects the socket
        return None
    try:
        conn = get_connection()
    except Exception:  # noqa: BLE001 — DB unavailable
        return None
    try:
        row = conn.execute(
            "SELECT id, username, role FROM students WHERE id=?", (claims.get("sub"),)
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        return None
    return {**claims, "sub": row["id"], "username": row["username"], "role": row["role"]}


def _task_exists(task_id: str) -> bool:
    try:
        conn = get_connection()
    except Exception:  # noqa: BLE001
        return False
    try:
        return (
            conn.execute("SELECT 1 FROM tasks WHERE id=? OR task_id=?", (task_id, task_id)).fetchone()
            is not None
        )
    finally:
        conn.close()


# === Snapshots (SQLite) ===


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def save_snapshot(room_name: str, ydoc: Y.YDoc) -> None:
    """Upsert the room's Y-state and plain text into collab_snapshots."""
    state = bytes(Y.encode_state_as_update(ydoc))
    text = str(ydoc.get_text("content"))
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO collab_snapshots (room, ystate, text, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(room) DO UPDATE SET
              ystate=excluded.ystate, text=excluded.text, updated_at=excluded.updated_at
            """,
            (room_name, state, text, _now_iso()),
        )
        conn.commit()
    finally:
        conn.close()


def load_snapshot(room_name: str) -> tuple[bytes, str] | None:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT ystate, text FROM collab_snapshots WHERE room=?", (room_name,)
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        return None
    return bytes(row["ystate"]), str(row["text"])


def _doc_from_text(text: str) -> Y.YDoc:
    ydoc = Y.YDoc()
    if text:
        ytext = ydoc.get_text("content")
        with ydoc.begin_transaction() as tx:
            ytext.insert(tx, 0, text)
    return ydoc


# === Collab server (WebsocketServer with snapshot hydration + idle sweep) ===

from ypy_websocket.websocket_server import WebsocketServer  # noqa: E402
from ypy_websocket.yroom import YRoom  # noqa: E402


class CollabWebsocketServer(WebsocketServer):
    """WebsocketServer hydrating fresh rooms from collab_snapshots."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._hydrated: set[str] = set()

    async def get_room(self, name: str) -> YRoom:
        room = await super().get_room(name)
        if name not in self._hydrated:
            self._hydrated.add(name)
            snapshot = load_snapshot(name)
            if snapshot is not None:
                state, _ = snapshot
                if state:
                    # Apply on top of whatever the room already merged.
                    Y.apply_update(room.ydoc, state)
                    log.info("collab: hydrated room %s from snapshot (%d bytes)", name, len(state))
        return room


class CollabServer:
    """Owns the ws server lifecycle and the idle-snapshot sweeper task."""

    def __init__(self) -> None:
        self.ws = CollabWebsocketServer(rooms_ready=True, auto_clean_rooms=True, log=log)
        self._sweeper: asyncio.Task[None] | None = None
        self._stop = asyncio.Event()

    async def __aenter__(self) -> "CollabServer":
        await self.ws.__aenter__()
        self._stop = asyncio.Event()
        self._sweeper = asyncio.create_task(self._sweep_idle_rooms())
        return self

    async def __aexit__(self, *exc: object) -> None:
        self._stop.set()
        if self._sweeper is not None:
            self._sweeper.cancel()
            try:
                await self._sweeper
            except (asyncio.CancelledError, Exception):  # noqa: BLE001
                pass
            self._sweeper = None
        # Persist every live room before shutdown.
        for name, room in list(self.ws.rooms.items()):
            try:
                save_snapshot(name, room.ydoc)
            except Exception:  # noqa: BLE001 — best-effort snapshot
                log.exception("collab: shutdown snapshot failed for %s", name)
        await self.ws.__aexit__(*exc)  # type: ignore[arg-type]

    async def _sweep_idle_rooms(self) -> None:
        interval = max(5.0, settings.collab_snapshot_interval_seconds)
        while not self._stop.is_set():
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=interval)
                break  # stop set
            except asyncio.TimeoutError:
                pass
            for name, room in list(self.ws.rooms.items()):
                try:
                    save_snapshot(name, room.ydoc)
                except Exception:  # noqa: BLE001
                    log.exception("collab: snapshot failed for %s", name)


# === ASGI wiring (ws auth + room ACL) ===



def _room_from_scope_path(path: str) -> str | None:
    """Extract the room name from the mounted scope path.

    The app is mounted at ``/collab/ws`` so scope['path'] inside the sub-app
    is the remainder, e.g. ``/pair:F1:abc``. Absolute-form paths
    (``/collab/ws/pair:F1:abc``) are accepted too for robustness.
    """
    prefix = "/collab/ws/"
    raw = path.lstrip("/")
    if raw.startswith("collab/ws/"):
        raw = raw[len(prefix) - 1 :]
    room = raw.strip("/")
    return room or None


def make_ws_asgi(collab: CollabServer):
    """Build the ASGI callable with auth+ACL on the connect handshake.

    Rejection sends an explicit ``websocket.close`` (4400-4499: terminal for
    y-websocket v3, so clients do not reconnect-loop on auth failures).
    """
    from ypy_websocket.asgi_server import ASGIWebsocket

    class _PathWebsocket(ASGIWebsocket):
        """ASGIWebsocket reporting the room name (not the mount path) as path."""

        def __init__(self, receive, send, path: str):
            super().__init__(receive, send, path)


    def _check(msg: dict, scope: dict) -> tuple[bool, int, str]:
        """Return (reject?, close_code, reason)."""
        query = scope.get("query_string", b"").decode("utf-8", "replace")
        params = dict(part.split("=", 1) for part in query.split("&") if "=" in part)
        from urllib.parse import unquote

        token = unquote(params.get("token", ""))
        user = _ws_user(token)
        if user is None:
            return (True, 4401, "auth required")
        room_name = _room_from_scope_path(scope.get("path", ""))
        if not room_name:
            return (True, 4400, "no room")
        try:
            spec = parse_room(room_name)
        except ValueError:
            log.warning("collab ws: rejected (room) %r", room_name)
            return (True, 4400, "bad room")
        if not _task_exists(spec.task_id):
            log.warning("collab ws: rejected (unknown task) %r", spec.task_id)
            return (True, 4404, "unknown task")
        if not room_allowed(user, spec):
            log.info(
                "collab ws: rejected (acl) room=%s user=%s role=%s",
                room_name,
                user.get("username"),
                user.get("role"),
            )
            return (True, 4403, "forbidden room")
        return (False, 0, "")

    async def app(scope: dict, receive, send):
        msg = await receive()
        if msg["type"] != "websocket.connect":
            return
        reject, code, reason = _check(msg, scope)
        if reject:
            await send({"type": "websocket.close", "code": code, "reason": reason})
            return
        await send({"type": "websocket.accept"})
        # WebsocketServer keys rooms by websocket.path — strip the mount
        # prefix so rooms match the canonical 'scenario:taskId:fileKey' names
        # used by snapshots and the REST API.
        room_name = _room_from_scope_path(scope.get("path", "")) or scope.get("path", "")
        websocket = _PathWebsocket(receive, send, room_name)
        await collab.ws.serve(websocket)

    return app


# === REST endpoints ===


class CollabResetRequest(BaseModel):
    content: str = Field(default="", max_length=4_000_000)


def create_collab_router(collab: CollabServer) -> APIRouter:
    router = APIRouter()

    @router.get("/collab/rooms/{room}/snapshot")
    async def room_snapshot(room: str, user: CurrentUser) -> dict:
        try:
            spec = parse_room(room)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        if not room_allowed(user, spec):
            raise HTTPException(status_code=403, detail="No access to this room")
        live = collab.ws.rooms.get(room)
        if live is not None:
            text = str(live.ydoc.get_text("content"))
            return {"room": room, "text": text, "updated_at": _now_iso(), "live": True}
        snapshot = load_snapshot(room)
        if snapshot is None:
            raise HTTPException(status_code=404, detail="Room has no snapshot yet")
        _, text = snapshot
        return {"room": room, "text": text, "updated_at": None, "live": False}

    @router.post(
        "/collab/rooms/{room}/reset",
        dependencies=[Depends(require_role("mentor", "admin"))],
    )
    async def room_reset(room: str, body: CollabResetRequest) -> dict:
        try:
            parse_room(room)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        if len(body.content.encode("utf-8")) > settings.collab_max_room_text_bytes:
            raise HTTPException(status_code=413, detail="Content exceeds the collab size limit")
        # Kill the live room so late clients hydrate from the new snapshot.
        if room in collab.ws.rooms:
            try:
                collab.ws.delete_room(name=room)
            except Exception:  # noqa: BLE001
                log.exception("collab: reset could not stop live room %s", room)
            collab.ws._hydrated.discard(room)  # noqa: SLF001 — allow re-hydration
        ydoc = _doc_from_text(body.content)
        save_snapshot(room, ydoc)
        return {"ok": True, "room": room}

    return router


# === App wiring ===


def setup_collab(app: FastAPI, collab: CollabServer) -> None:
    """Register REST routes and mount the ws ASGI sub-app."""
    app.include_router(create_collab_router(collab), tags=["collab"])
    app.mount("/collab/ws", make_ws_asgi(collab))


def get_collab_server() -> CollabServer:
    """Process-wide singleton (survives test reloads of ego_server.main)."""
    import ego_server.collab as _self

    if getattr(_self, "_collab_server", None) is None:
        _self._collab_server = CollabServer()
    return _self._collab_server
