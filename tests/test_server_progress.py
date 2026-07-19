"""Tests for ego_server progress router — POST /progress/push, GET /progress/<id>."""

from __future__ import annotations

import importlib
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def temp_db(monkeypatch):
    tmp = Path(tempfile.mkdtemp()) / "test.db"
    monkeypatch.setenv("EGO_DB_PATH", str(tmp))

    import ego_server.config
    import ego_server.db

    importlib.reload(ego_server.config)
    importlib.reload(ego_server.db)

    from ego_server.db import init_db

    init_db()
    yield tmp


@pytest.fixture
def client(temp_db, monkeypatch):
    repo_root = Path(__file__).parent.parent
    monkeypatch.chdir(repo_root)

    import ego_server.main

    importlib.reload(ego_server.main)
    from ego_server.main import app

    # Import tasks so they exist in DB.
    from ego_server.cli import main as cli_main

    cli_main(["admin", "import-tasks", "--docs-dir", "docs/tasks"])

    with TestClient(app) as c:
        yield c


def _register_and_login(client, username="alice", password="pw", role="student"):
    r = client.post(
        "/auth/register",
        json={"username": username, "password": password, "role": role},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"], r.json()["user_id"]


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# === POST /progress/push ===


def test_push_requires_auth(client):
    r = client.post("/progress/push", json={})
    assert r.status_code == 401


def test_push_success(client):
    token, student_id = _register_and_login(client)
    r = client.post(
        "/progress/push",
        json={
            "task_id": "F1",
            "version": "1.0.0",
            "solution_hash": "a" * 64,
            "status": "passed",
            "log": "all good",
            "passed_tests": 3,
            "total_tests": 3,
        },
        headers=_auth_headers(token),
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["student_id"] == student_id
    assert data["task_id"] == "F1"
    assert data["version"] == "1.0.0"
    assert data["status"] == "passed"
    assert data["attempts"] == 1
    assert data["passed_tests"] == 3
    assert data["total_tests"] == 3


def test_push_increments_attempts(client):
    token, _ = _register_and_login(client)
    body = {
        "task_id": "F1",
        "version": "1.0.0",
        "solution_hash": "a" * 64,
        "status": "failed",
        "log": "first attempt",
        "passed_tests": 1,
        "total_tests": 3,
    }
    r1 = client.post("/progress/push", json=body, headers=_auth_headers(token))
    assert r1.status_code == 200
    assert r1.json()["attempts"] == 1

    body["status"] = "passed"
    body["passed_tests"] = 3
    r2 = client.post("/progress/push", json=body, headers=_auth_headers(token))
    assert r2.status_code == 200
    assert r2.json()["attempts"] == 2
    assert r2.json()["status"] == "passed"


def test_push_task_not_found_404(client):
    token, _ = _register_and_login(client)
    r = client.post(
        "/progress/push",
        json={
            "task_id": "ZZZ",
            "version": "1.0.0",
            "solution_hash": "a" * 64,
            "status": "passed",
            "log": "",
            "passed_tests": 0,
            "total_tests": 0,
        },
        headers=_auth_headers(token),
    )
    assert r.status_code == 404


def test_push_empty_solution_hash_422(client):
    token, _ = _register_and_login(client)
    r = client.post(
        "/progress/push",
        json={
            "task_id": "F1",
            "version": "1.0.0",
            "solution_hash": "",
            "status": "passed",
            "log": "",
            "passed_tests": 0,
            "total_tests": 0,
        },
        headers=_auth_headers(token),
    )
    assert r.status_code == 422


def test_push_writes_run_log(client, temp_db):
    """After push, runs table should have a row."""
    import sqlite3

    token, student_id = _register_and_login(client)
    client.post(
        "/progress/push",
        json={
            "task_id": "F1",
            "version": "1.0.0",
            "solution_hash": "b" * 64,
            "status": "passed",
            "log": "test log content",
            "passed_tests": 2,
            "total_tests": 2,
        },
        headers=_auth_headers(token),
    )
    conn = sqlite3.connect(temp_db)
    rows = conn.execute("SELECT * FROM runs WHERE student_id = ?", (student_id,)).fetchall()
    conn.close()
    assert len(rows) == 1
    # Check log content.
    assert "test log content" in rows[0][6]  # log column


def test_push_truncates_long_log(client, temp_db):
    """Log should be truncated to 8KB."""
    import sqlite3

    token, _ = _register_and_login(client)
    long_log = "x" * 20000
    client.post(
        "/progress/push",
        json={
            "task_id": "F1",
            "version": "1.0.0",
            "solution_hash": "c" * 64,
            "status": "passed",
            "log": long_log,
            "passed_tests": 0,
            "total_tests": 0,
        },
        headers=_auth_headers(token),
    )
    conn = sqlite3.connect(temp_db)
    row = conn.execute("SELECT log FROM runs").fetchone()
    conn.close()
    assert len(row[0]) <= 8192


# === GET /progress/<student_id> ===


def test_get_progress_requires_mentor(client):
    """Student should get 403 when trying to view progress."""
    token, student_id = _register_and_login(client, role="student")
    r = client.get(f"/progress/{student_id}", headers=_auth_headers(token))
    assert r.status_code == 403


def test_get_progress_mentor_can_view(client):
    token, student_id = _register_and_login(client, role="student")
    # Push some progress.
    client.post(
        "/progress/push",
        json={
            "task_id": "F1",
            "version": "1.0.0",
            "solution_hash": "d" * 64,
            "status": "passed",
            "log": "",
            "passed_tests": 3,
            "total_tests": 3,
        },
        headers=_auth_headers(token),
    )
    # Mentor views.
    m_token, _ = _register_and_login(client, role="mentor", username="mentor1")
    r = client.get(f"/progress/{student_id}", headers=_auth_headers(m_token))
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["task_id"] == "F1"
    assert data[0]["status"] == "passed"


def test_get_progress_empty(client):
    """Mentor views student with no progress → empty list."""
    token, student_id = _register_and_login(client, role="student")
    m_token, _ = _register_and_login(client, role="mentor", username="mentor2")
    r = client.get(f"/progress/{student_id}", headers=_auth_headers(m_token))
    assert r.status_code == 200
    assert r.json() == []


def test_get_progress_unauth_401(client):
    r = client.get("/progress/some-id")
    assert r.status_code == 401


def test_get_progress_admin_can_view(client):
    token, student_id = _register_and_login(client, role="student")
    client.post(
        "/progress/push",
        json={
            "task_id": "F1",
            "version": "1.0.0",
            "solution_hash": "e" * 64,
            "status": "failed",
            "log": "",
            "passed_tests": 1,
            "total_tests": 3,
        },
        headers=_auth_headers(token),
    )
    a_token, _ = _register_and_login(client, role="admin", username="admin1")
    r = client.get(f"/progress/{student_id}", headers=_auth_headers(a_token))
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["status"] == "failed"
