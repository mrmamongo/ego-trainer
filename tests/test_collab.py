"""Collaborative editing server tests (ADR-0017 P1).

Covers: room grammar, scenario ACL, snapshot REST contract, websocket
handshake auth/room rejection, and snapshot persistence of room text.
"""

from __future__ import annotations

import importlib
import tempfile
from pathlib import Path

import pytest
import y_py as Y
from fastapi.testclient import TestClient


@pytest.fixture
def temp_db(monkeypatch):
    """Fresh temp SQLite DB with schema applied."""
    tmp = Path(tempfile.mkdtemp()) / "test.db"
    monkeypatch.setenv("EGO_DB_PATH", str(tmp))
    monkeypatch.setenv("EGO_COLLAB_ENABLED", "true")

    import ego_server.config
    import ego_server.db

    importlib.reload(ego_server.config)
    importlib.reload(ego_server.db)

    from ego_server.db import init_db

    init_db()
    yield tmp


@pytest.fixture
def client(temp_db, monkeypatch):
    """TestClient with collab enabled and one task imported (F2)."""
    repo_root = Path(__file__).parent.parent
    monkeypatch.chdir(repo_root)

    import ego_server.main

    importlib.reload(ego_server.main)
    from ego_server.main import app

    from ego_server.cli import main as cli_main

    cli_main(["admin", "import-tasks", "--docs-dir", "docs/tasks"])

    with TestClient(app) as c:
        yield c


def _student_token(client: TestClient) -> str:
    import uuid

    r = client.post(
        "/auth/register",
        json={"username": f"stu_{uuid.uuid4().hex[:8]}", "password": "pw-collab-1"},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def _mentor_token(client: TestClient, temp_db: Path) -> str:
    """Create a mentor directly in the DB, then log in via local auth."""
    from ego_server.auth import create_token, generate_user_id
    from ego_server.db import get_connection

    conn = get_connection()
    try:
        user_id = generate_user_id()
        conn.execute(
            "INSERT INTO students (id, username, role, password_hash, created_at) "
            "VALUES (?, ?, 'mentor', '', ?)",
            (user_id, f"ment_{user_id[:8]}", __import__("datetime").datetime.now(
                __import__("datetime").UTC).isoformat()),
        )
        conn.commit()
    finally:
        conn.close()
    return create_token(user_id=user_id, username=f"ment_{user_id[:8]}", role="mentor")


# === Room grammar ===


def test_parse_room_valid_and_invalid():
    from ego_server.collab import parse_room

    spec = parse_room("studio:F2:markdown")
    assert (spec.scenario, spec.task_id, spec.file_key) == ("studio", "F2", "markdown")
    assert parse_room("pair:F1:abc_123").scenario == "pair"

    with pytest.raises(ValueError):
        parse_room("nonsense")
    with pytest.raises(ValueError):
        parse_room("vault:F1:x")  # unknown scenario
    with pytest.raises(ValueError):
        parse_room("studio:F2:readme")  # bad studio file key
    with pytest.raises(ValueError):
        parse_room("pair:F1:bad key!")  # bad free file key
    with pytest.raises(ValueError):
        parse_room("pair::nofile")  # empty task id


def test_room_allowed_matrix():
    from ego_server.collab import parse_room, room_allowed

    student = {"role": "student"}
    mentor = {"role": "mentor"}
    admin = {"role": "admin"}

    assert room_allowed(student, parse_room("pair:F1:main"))
    assert room_allowed(student, parse_room("defense:F1:main"))
    assert not room_allowed(student, parse_room("studio:F1:markdown"))
    assert room_allowed(mentor, parse_room("studio:F1:markdown"))
    assert room_allowed(admin, parse_room("studio:F1:solution_py"))


# === REST snapshot endpoints ===


def test_snapshot_requires_auth(client: TestClient):
    r = client.get("/collab/rooms/pair:F2:main/snapshot")
    assert r.status_code == 401


def test_snapshot_404_for_unknown_room(client: TestClient):
    token = _student_token(client)
    r = client.get(
        "/collab/rooms/pair:F2:mains/snapshot", headers={"Authorization": f"Bearer {token}"}
    )
    # Valid room name but no snapshot yet.
    assert r.status_code == 404


def test_snapshot_malformed_room_422(client: TestClient):
    token = _student_token(client)
    r = client.get(
        "/collab/rooms/not-a-room/snapshot", headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 422


def test_reset_requires_mentor(client: TestClient, temp_db: Path):
    token = _student_token(client)
    r = client.post(
        "/collab/rooms/pair:F2:main/reset",
        json={"content": "hello"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403

    mentor = _mentor_token(client, temp_db)
    r = client.post(
        "/collab/rooms/pair:F2:main/reset",
        json={"content": "hello"},
        headers={"Authorization": f"Bearer {mentor}"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["ok"] is True

    # Snapshot is now readable by the student (pair rooms allow students).
    r = client.get(
        "/collab/rooms/pair:F2:main/snapshot",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["text"] == "hello"


def test_reset_size_limit(client: TestClient, temp_db: Path):
    mentor = _mentor_token(client, temp_db)
    big = "x" * (1_000_001)
    r = client.post(
        "/collab/rooms/pair:F2:main/reset",
        json={"content": big},
        headers={"Authorization": f"Bearer {mentor}"},
    )
    assert r.status_code == 413


# === WebSocket handshake ===


def test_ws_rejects_missing_token(client: TestClient):
    with pytest.raises(Exception):  # noqa: BLE001 — any close/disconnect
        with client.websocket_connect("/collab/ws/pair:F2:main"):
            pass


def test_ws_rejects_bad_room(client: TestClient):
    token = _student_token(client)
    with pytest.raises(Exception):  # noqa: BLE001
        with client.websocket_connect(f"/collab/ws/pair:F2:bad key!?token={token}"):
            pass


def _sync_step1(ydoc: Y.YDoc | None = None) -> bytes:
    """Valid sync-step-1 frame via the ypy-websocket factories."""
    from ypy_websocket.yutils import create_sync_step1_message

    doc = ydoc or Y.YDoc()
    return bytes(create_sync_step1_message(bytes(Y.encode_state_vector(doc))))


def _receive_until(ws, prefix: bytes, limit: int = 10) -> bytes:
    """Read ws frames until one starts with prefix (skips server step-1 pings)."""
    import time

    for _ in range(limit):
        frame = ws.receive_bytes()
        if frame.startswith(prefix):
            return frame
        time.sleep(0.05)
    raise AssertionError(f"no frame with prefix {prefix!r} within {limit} frames")


def test_ws_accepts_pair_room_for_student(client: TestClient):
    token = _student_token(client)
    with client.websocket_connect(f"/collab/ws/pair:F2:main?token={token}") as ws:
        # The server initiates the yjs sync: first incoming frame is its
        # sync step-1 (0x00 0x00 <varuint len> <state vector>).
        first = ws.receive_bytes()
        assert first[:2] == b"\x00\x00"
        # Reply with our valid sync step-1 — the server answers (possibly
        # after echoing its own step-1) with sync step-2 (0x00 0x01 ...).
        ws.send_bytes(_sync_step1())
        reply = _receive_until(ws, b"\x00\x01")
        assert reply[:2] == b"\x00\x01"


def test_ws_rejects_studio_room_for_student(client: TestClient):
    token = _student_token(client)
    with pytest.raises(Exception):  # noqa: BLE001
        with client.websocket_connect(f"/collab/ws/studio:F2:markdown?token={token}"):
            pass


# === Snapshot persistence via ws writes ===


def test_ws_update_persists_snapshot(client: TestClient, temp_db: Path):
    from ego_server.collab import load_snapshot, save_snapshot
    from ypy_websocket.yutils import create_update_message

    token = _student_token(client)
    with client.websocket_connect(f"/collab/ws/pair:F2:persist?token={token}") as ws:
        ws.receive_bytes()  # server sync step-1
        # Build a Y update that inserts text, locally.
        ydoc = Y.YDoc()
        ytext = ydoc.get_text("content")
        with ydoc.begin_transaction() as tx:
            ytext.insert(tx, 0, "hello collab")
        update = bytes(Y.encode_state_as_update(ydoc))
        ws.send_bytes(bytes(create_update_message(update)))
        import time

        time.sleep(0.5)
        ws.send_bytes(_sync_step1())  # force another sync round
        _receive_until(ws, b"\x00\x01")

        # Read the live room through the REST API: it touches the room YDoc
        # on the server's thread only (direct ydoc access from the test
        # thread panics in y-py during concurrent transactions).
        r = client.get(
            "/collab/rooms/pair:F2:persist/snapshot",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["live"] is True
        assert "hello collab" in body["text"]

    # The sweeper path: persist a rebuilt doc and read it back via the API.
    seed = Y.YDoc()
    seed_text = seed.get_text("content")
    with seed.begin_transaction() as tx:
        seed_text.insert(tx, 0, body["text"])
    save_snapshot("pair:F2:persist", seed)
    _, snap_text = load_snapshot("pair:F2:persist")
    assert "hello collab" in snap_text
    r = client.get(
        "/collab/rooms/pair:F2:persist/snapshot",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert "hello collab" in r.json()["text"]
