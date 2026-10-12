"""Collaborative editing server tests (ADR-0017 P1).

Covers: room grammar, scenario ACL matrix, snapshot REST contract, ws
handshake auth/ACL, yjs sync protocol smoke, and snapshot persistence.
"""

from __future__ import annotations

import importlib
import tempfile
import time
from pathlib import Path

import pytest
import y_py as Y
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

pytest.importorskip("ypy_websocket", reason="collab extra not installed")

REPO_ROOT = Path(__file__).parent.parent


# === Fixtures (following tests/test_server_tasks.py) ===


@pytest.fixture
def temp_db(monkeypatch):
    """Fresh temp SQLite DB with schema applied, collab enabled."""
    tmp = Path(tempfile.mkdtemp()) / "test.db"
    monkeypatch.setenv("EGO_DB_PATH", str(tmp))
    monkeypatch.setenv("EGO_COLLAB_ENABLED", "true")
    monkeypatch.delenv("EGO_MCP_ENABLED", raising=False)

    import ego_server.collab
    import ego_server.config
    import ego_server.db

    importlib.reload(ego_server.config)
    importlib.reload(ego_server.db)
    importlib.reload(ego_server.collab)

    from ego_server.db import init_db

    init_db()
    yield tmp


@pytest.fixture
def client(temp_db, monkeypatch):
    """TestClient with collab enabled and tasks imported from docs/tasks/."""
    monkeypatch.chdir(REPO_ROOT)

    import ego_server.main

    importlib.reload(ego_server.main)
    from ego_server.main import app

    from ego_server.cli import main as cli_main

    cli_main(["admin", "import-tasks", "--docs-dir", "docs/tasks"])

    with TestClient(app) as c:
        yield c


def _student_token(client: TestClient, username: str = "stu_collab") -> str:
    r = client.post("/auth/register", json={"username": username, "password": "pw-collab-1"})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def _role_token(client: TestClient, username: str, role: str) -> str:
    from tests.conftest import create_test_user

    token, _ = create_test_user(client, username, "pw-collab-1", role)
    return token


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# === Yjs wire helpers ===
#
# ypy-websocket framing (ypy_websocket.yutils):
#   message   = message_type (1 byte) + varuint(len) + payload
#   sync payload = sync_step (1 byte) + varuint(len) + data
# message_type: 0=SYNC, 1=AWARENESS; sync_step: 0=STEP1, 1=STEP2, 2=UPDATE.


def _varuint(n: int) -> bytes:
    out = bytearray()
    while n > 0x7F:
        out.append((n & 0x7F) | 0x80)
        n >>= 7
    out.append(n)
    return bytes(out)


def _sync(step: int, data: bytes) -> bytes:
    return b"\x00" + bytes([step]) + _varuint(len(data)) + data


# Пустой state vector от y_py — один байт 0x00 (не пустая строка! y_py
# бросает EncodingException на нулевую длину).
_SYNC_STEP1_EMPTY = _sync(0, b"\x00")


def _parse_sync(frame: bytes) -> tuple[int, bytes]:
    """Return (sync_step, data) of a SYNC frame; AssertionError otherwise."""
    assert frame[0] == 0, f"not a SYNC frame: {frame[:4]!r}"
    step = frame[1]
    length = 0
    i = 2
    shift = 0
    while True:
        b = frame[i]
        length |= (b & 0x7F) << shift
        shift += 7
        i += 1
        if b < 0x80:
            break
    return step, frame[i : i + length]


def _receive_sync_step2(ws, timeout_s: float = 5.0) -> bytes:
    """Read frames until the server's SYNC_STEP2 reply lands; return its data.

    The server may first send its own step-1 (fresh doc state vector) and the
    empty-update broadcast (y-py #98), so order is not guaranteed.
    """
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        step, data = _parse_sync(ws.receive_bytes())
        if step == 1:
            return data
    raise AssertionError("no SYNC_STEP2 reply within timeout")


def _local_text(update: bytes) -> str:
    """Apply a server update to a fresh local doc and read back the text."""
    local = Y.YDoc()
    if update and update != b"\x00\x00":
        Y.apply_update(local, update)
    return str(local.get_text("content"))


# === Room grammar (parse_room) ===


def test_parse_room_grammar():
    from ego_server.collab import parse_room

    spec = parse_room("studio:F2:markdown")
    assert (spec.scenario, spec.task_id, spec.file_key) == ("studio", "F2", "markdown")
    assert parse_room("pair:F1:main-A_2").scenario == "pair"
    assert parse_room("defense:1.5:room").task_id == "1.5"

    for bad in (
        "nonsense",  # wrong shape
        "vault:F1:x",  # unknown scenario
        "studio:F2:readme",  # studio file key outside the whitelist
        "pair:F1:bad key!",  # free file key with forbidden chars
        "pair::nofile",  # empty task id
        "pair:F1",  # missing segment
        "a:b:c:d",  # extra segment
    ):
        with pytest.raises(ValueError):
            parse_room(bad)


def test_parse_room_task_id_charset():
    from ego_server.collab import parse_room

    with pytest.raises(ValueError):
        parse_room("pair:F/1:main")  # path separators are not task ids
    assert parse_room("studio:A-1.b:solution_py").file_key == "solution_py"


# === ACL matrix (room_allowed) ===


def test_room_allowed_matrix():
    from ego_server.collab import parse_room, room_allowed

    student = {"role": "student"}
    mentor = {"role": "mentor"}
    admin = {"role": "admin"}

    # studio → mentor/admin only
    assert not room_allowed(student, parse_room("studio:F1:markdown"))
    assert room_allowed(mentor, parse_room("studio:F1:markdown"))
    assert room_allowed(admin, parse_room("studio:F1:tests_py"))

    # defense → any authenticated user
    assert room_allowed(student, parse_room("defense:F1:main"))
    assert room_allowed(mentor, parse_room("defense:F1:main"))
    assert room_allowed(admin, parse_room("defense:F1:main"))

    # pair → any authenticated user
    assert room_allowed(student, parse_room("pair:F1:main"))
    assert room_allowed(mentor, parse_room("pair:F1:main"))
    assert room_allowed(admin, parse_room("pair:F1:main"))


def test_room_allowed_malformed_room_raises():
    from ego_server.collab import parse_room

    with pytest.raises(ValueError):
        parse_room("not-a-room")  # ws: rejected by the handshake gate


# === REST: snapshot endpoint ===


def test_snapshot_requires_auth(client: TestClient):
    r = client.get("/collab/rooms/pair:F2:main/snapshot")
    assert r.status_code == 401


def test_snapshot_404_when_no_snapshot_and_no_room(client: TestClient):
    token = _student_token(client)
    r = client.get("/collab/rooms/pair:F2:main/snapshot", headers=_auth(token))
    assert r.status_code == 404


def test_snapshot_returns_seeded_text_after_reset(client: TestClient):
    mentor = _role_token(client, "mentor_collab", "mentor")
    r = client.post(
        "/collab/rooms/pair:F2:main/reset",
        json={"content": "# seeded text"},
        headers=_auth(mentor),
    )
    assert r.status_code == 200, r.text
    assert r.json() == {"ok": True}

    token = _student_token(client)
    r = client.get("/collab/rooms/pair:F2:main/snapshot", headers=_auth(token))
    assert r.status_code == 200
    data = r.json()
    assert data["room"] == "pair:F2:main"
    assert data["text"] == "# seeded text"
    assert data["updated_at"]


# === REST: reset authorization ===


def test_reset_student_gets_403(client: TestClient):
    token = _student_token(client)
    r = client.post(
        "/collab/rooms/pair:F2:main/reset",
        json={"content": "x"},
        headers=_auth(token),
    )
    assert r.status_code == 403


def test_reset_mentor_and_admin_ok(client: TestClient):
    for i, role in enumerate(("mentor", "admin")):
        token = _role_token(client, f"{role}_collab_{i}", role)
        r = client.post(
            "/collab/rooms/pair:F2:main/reset",
            json={"content": f"content from {role}"},
            headers=_auth(token),
        )
        assert r.status_code == 200, r.text


def test_reset_requires_auth(client: TestClient):
    r = client.post("/collab/rooms/pair:F2:main/reset", json={"content": "x"})
    assert r.status_code == 401


def test_reset_size_limit_413(client: TestClient):
    mentor = _role_token(client, "mentor_limit", "mentor")
    big = "x" * (1_000_001)
    r = client.post(
        "/collab/rooms/pair:F2:main/reset", json={"content": big}, headers=_auth(mentor)
    )
    assert r.status_code == 413


def test_reset_malformed_room_422(client: TestClient):
    mentor = _role_token(client, "mentor_bad_room", "mentor")
    r = client.post("/collab/rooms/not-a-room/reset", json={"content": "x"}, headers=_auth(mentor))
    assert r.status_code == 422


# === ws smoke: auth / room validation / ACL ===


def test_ws_rejected_without_token(client: TestClient):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/collab/ws/pair:F2:main"):
            pass


def test_ws_rejected_with_garbage_token(client: TestClient):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/collab/ws/pair:F2:main?token=garbage"):
            pass


def test_ws_rejected_bad_room_name(client: TestClient):
    token = _student_token(client)
    # Space in the URL-encoded room name is invalid for the free-key grammar.
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(f"/collab/ws/pair:F2:bad%20key?token={token}"):
            pass


def test_ws_rejected_unknown_task(client: TestClient):
    token = _student_token(client)
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(f"/collab/ws/pair:ZZZ999:main?token={token}"):
            pass


def test_ws_rejected_studio_room_for_student(client: TestClient):
    token = _student_token(client)
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(f"/collab/ws/studio:F2:markdown?token={token}"):
            pass


def test_ws_studio_room_ok_for_mentor(client: TestClient):
    mentor = _role_token(client, "mentor_ws", "mentor")
    with client.websocket_connect(f"/collab/ws/studio:F2:markdown?token={mentor}") as ws:
        ws.send_bytes(_SYNC_STEP1_EMPTY)
        _receive_sync_step2(ws)


def test_ws_pair_room_accepts_student_and_syncs(client: TestClient):
    token = _student_token(client)
    with client.websocket_connect(f"/collab/ws/pair:F2:main?token={token}") as ws:
        ws.send_bytes(_SYNC_STEP1_EMPTY)
        update = _receive_sync_step2(ws)
        # Empty room: the minimal update from y_py (y-py #98) or bigger.
        assert isinstance(update, bytes)


# === ws: sync reply carries hydrated snapshot content ===


def test_ws_step2_carries_snapshot_text(client: TestClient):
    mentor = _role_token(client, "mentor_hydr", "mentor")
    r = client.post(
        "/collab/rooms/pair:F2:doc/reset",
        json={"content": "hydrated content"},
        headers=_auth(mentor),
    )
    assert r.status_code == 200

    token = _student_token(client, "stu_hydr")
    with client.websocket_connect(f"/collab/ws/pair:F2:doc?token={token}") as ws:
        ws.send_bytes(_SYNC_STEP1_EMPTY)
        update = _receive_sync_step2(ws)
        assert _local_text(update) == "hydrated content"


# === Snapshot persistence: ws update -> room cleanup -> REST read ===


def test_reset_while_room_live_replaces_snapshot(client: TestClient):
    """Reset with a client connected: room stopped, snapshot replaced, no crash."""
    student = _student_token(client, "stu_live_reset")
    mentor = _role_token(client, "mentor_live_reset", "mentor")
    with client.websocket_connect(f"/collab/ws/pair:F2:live?token={student}") as ws:
        ws.send_bytes(_SYNC_STEP1_EMPTY)
        _receive_sync_step2(ws)

        # Reset with the room live: deletes the room (snapshot on delete) and
        # overwrites the snapshot with the fresh content.
        r = client.post(
            "/collab/rooms/pair:F2:live/reset",
            json={"content": "reset while live"},
            headers=_auth(mentor),
        )
        assert r.status_code == 200, r.text

    from ego_server.collab import get_collab_server

    collab = get_collab_server()
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline and "pair:F2:live" in collab.ws.rooms:
        time.sleep(0.05)
    assert "pair:F2:live" not in collab.ws.rooms

    r = client.get("/collab/rooms/pair:F2:live/snapshot", headers=_auth(student))
    assert r.status_code == 200
    assert r.json()["text"] == "reset while live"


def test_ws_update_persists_to_snapshot(client: TestClient):
    token = _student_token(client, "stu_persist")
    with client.websocket_connect(f"/collab/ws/pair:F2:persist?token={token}") as ws:
        ws.send_bytes(_SYNC_STEP1_EMPTY)
        _receive_sync_step2(ws)

        # Local doc with text; send its full state as a SYNC UPDATE (step 2).
        ydoc = Y.YDoc()
        ytext = ydoc.get_text("content")
        with ydoc.begin_transaction() as tx:
            ytext.insert(tx, 0, "hello")
        update = bytes(Y.encode_state_as_update(ydoc))
        ws.send_bytes(_sync(2, update))
        # Дождаться применения: step-1 → step-2 echo содержит наш текст.
        ws.send_bytes(_SYNC_STEP1_EMPTY)
        echoed = _receive_sync_step2(ws)
        assert _local_text(echoed) == "hello"

    # Room auto-clean on last-client exit persists the snapshot (the
    # delete_room override); give the event loop a beat to run the cleanup.
    from ego_server.collab import get_collab_server

    collab = get_collab_server()
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline and "pair:F2:persist" in collab.ws.rooms:
        time.sleep(0.05)
    assert "pair:F2:persist" not in collab.ws.rooms

    r = client.get("/collab/rooms/pair:F2:persist/snapshot", headers=_auth(token))
    assert r.status_code == 200, r.text
    assert r.json()["text"] == "hello"


def test_save_snapshot_direct_roundtrip(client: TestClient):
    """Direct _save_snapshot with a room-like doc; REST reads it back."""
    from ego_server.collab import _save_snapshot

    ydoc = Y.YDoc()
    ytext = ydoc.get_text("content")
    with ydoc.begin_transaction() as tx:
        ytext.insert(tx, 0, "direct hello")
    _save_snapshot("pair:F2:direct", ydoc)

    token = _student_token(client, "stu_direct")
    r = client.get("/collab/rooms/pair:F2:direct/snapshot", headers=_auth(token))
    assert r.status_code == 200
    assert r.json()["text"] == "direct hello"


# === Collab disabled by default: no routes mounted ===


def test_collab_disabled_by_default(monkeypatch):
    """Default settings: no collab routes, app works identically."""
    import ego_server.collab
    import ego_server.config
    import ego_server.main

    monkeypatch.delenv("EGO_COLLAB_ENABLED", raising=False)
    importlib.reload(ego_server.config)
    importlib.reload(ego_server.collab)
    importlib.reload(ego_server.main)
    from ego_server.main import app

    assert ego_server.config.settings.collab_enabled is False
    paths = {getattr(r, "path", "") for r in app.routes}
    assert not any("/collab" in p for p in paths)

    with TestClient(app) as c:
        assert c.get("/health").status_code == 200


# === Share-комнаты: вход по непрозрачной ссылке ===


def test_share_room_lifecycle(client: TestClient):
    """Создание (mentor) → чтение по id → закрытие создателем → 404 после."""
    mentor = _role_token(client, "share_mentor", "mentor")
    student = _student_token(client, "share_stu")

    # Создание — только mentor/admin.
    r = client.post("/collab/share", json={"task_id": "F2"}, headers=_auth(student))
    assert r.status_code == 403
    r = client.post(
        "/collab/share",
        json={"task_id": "F2", "title": "Разбор F2"},
        headers=_auth(mentor),
    )
    assert r.status_code == 200, r.text
    data = r.json()
    room_id = data["room_id"]
    assert data["task_id"] == "F2"
    assert data["title"] == "Разбор F2"
    assert data["active"] is True

    # Чтение метаданных — любой авторизованный с валидным id (ссылка = capability).
    r = client.get(f"/collab/share/{room_id}", headers=_auth(student))
    assert r.status_code == 200
    assert r.json()["task_id"] == "F2"

    # Неизвестный id → 404; без auth → 401.
    assert client.get("/collab/share/doesnotexist1234", headers=_auth(student)).status_code == 404
    assert client.get(f"/collab/share/{room_id}").status_code == 401

    # Закрытие: не создатель → 403; создатель → ок; после закрытия get/ws → 404/закрыто.
    r = client.post(f"/collab/share/{room_id}/close", headers=_auth(student))
    assert r.status_code == 403
    r = client.post(f"/collab/share/{room_id}/close", headers=_auth(mentor))
    assert r.status_code == 200
    assert client.get(f"/collab/share/{room_id}", headers=_auth(student)).status_code == 404


def test_share_room_requires_known_task(client: TestClient):
    mentor = _role_token(client, "share_mentor2", "mentor")
    r = client.post("/collab/share", json={"task_id": "NOPE"}, headers=_auth(mentor))
    assert r.status_code == 404


def test_share_room_ws_accepted_then_rejected_after_close(client: TestClient):
    """ws в share-комнату: активная пускает, закрытая — нет."""
    mentor = _role_token(client, "share_mentor3", "mentor")
    student = _student_token(client, "share_stu3")
    room_id = client.post(
        "/collab/share", json={"task_id": "F2"}, headers=_auth(mentor)
    ).json()["room_id"]

    ws_room = f"share:{room_id}:main"
    with client.websocket_connect(f"/collab/ws/{ws_room}?token={student}") as ws:
        first = ws.receive_bytes()
        assert first[:2] == b"\x00\x00"

    client.post(f"/collab/share/{room_id}/close", headers=_auth(mentor))
    with pytest.raises(Exception):  # noqa: BLE001 — любое закрытие/дисконнект
        with client.websocket_connect(f"/collab/ws/{ws_room}?token={student}"):
            pass


def test_share_room_id_grammar():
    """share-слот требует capability-подобный id (не короткий/не угадываемый)."""
    from ego_server.collab import parse_room

    assert parse_room("share:abcdefghijklmnop:main").scenario == "share"
    with pytest.raises(ValueError):
        parse_room("share:short:main")  # <16 chars
    with pytest.raises(ValueError):
        parse_room("share:точка.невалидна:main")
