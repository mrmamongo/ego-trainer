"""Tests for ego_server tasks router — GET /tasks, GET /tasks/<id>."""

from __future__ import annotations

import importlib
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def temp_db(monkeypatch):
    """Fresh temp SQLite DB with schema applied."""
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
    """FastAPI TestClient with temp DB and 33 tasks imported from docs/tasks/."""
    repo_root = Path(__file__).parent.parent
    monkeypatch.chdir(repo_root)

    import ego_server.main

    importlib.reload(ego_server.main)
    from ego_server.main import app

    # Import tasks via ego-server CLI logic.
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
    return r.json()["access_token"]


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# === list ===


def test_list_tasks_requires_auth(client):
    r = client.get("/tasks")
    assert r.status_code == 401


def test_list_tasks_returns_33(client):
    token = _register_and_login(client)
    r = client.get("/tasks", headers=_auth_headers(token))
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 33


def test_list_tasks_filter_by_block(client):
    token = _register_and_login(client)
    r = client.get("/tasks?block=F", headers=_auth_headers(token))
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 5  # F1-F5
    assert all(t["block"] == "F" for t in data)


def test_list_tasks_filter_nonexistent_block_returns_empty(client):
    token = _register_and_login(client)
    r = client.get("/tasks?block=ZZZ", headers=_auth_headers(token))
    assert r.status_code == 200
    assert r.json() == []


# === get single task ===


def test_get_task_returns_full_without_solution_for_student(client):
    token = _register_and_login(client, role="student")
    r = client.get("/tasks/F1", headers=_auth_headers(token))
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == "F1"
    assert data["title"]
    assert data["statement_md"]
    assert data["stub_py"]
    assert data["solution_py"] == ""  # hidden from student


def test_get_task_with_include_solution_for_student_ignored(client):
    """Student requesting ?include_solution=true gets empty solution (ignored)."""
    token = _register_and_login(client, role="student")
    r = client.get("/tasks/F1?include_solution=true", headers=_auth_headers(token))
    assert r.status_code == 200
    data = r.json()
    assert data["solution_py"] == ""


def test_get_task_with_include_solution_for_mentor(client):
    token = _register_and_login(client, role="mentor", username="mentor1")
    r = client.get("/tasks/F1?include_solution=true", headers=_auth_headers(token))
    assert r.status_code == 200
    data = r.json()
    assert data["solution_py"]  # non-empty
    assert "def task_f1_find_critical" in data["solution_py"]


def test_get_task_not_found_404(client):
    token = _register_and_login(client)
    r = client.get("/tasks/ZZZ", headers=_auth_headers(token))
    assert r.status_code == 404


# === solution endpoint ===


def test_get_solution_endpoint_for_mentor(client):
    token = _register_and_login(client, role="mentor", username="mentor2")
    r = client.get("/tasks/F1/solution", headers=_auth_headers(token))
    assert r.status_code == 200
    data = r.json()
    assert data["task_id"] == "F1"
    assert "def task_f1_find_critical" in data["solution_py"]


def test_get_solution_endpoint_for_student_403(client):
    token = _register_and_login(client, role="student")
    r = client.get("/tasks/F1/solution", headers=_auth_headers(token))
    assert r.status_code == 403


def test_get_solution_unauth_401(client):
    r = client.get("/tasks/F1/solution")
    assert r.status_code == 401


# === meta fields ===


def test_list_tasks_has_version_field(client):
    token = _register_and_login(client)
    r = client.get("/tasks?block=A", headers=_auth_headers(token))
    data = r.json()
    assert data[0]["version"] == "1.0.0"  # initial import


def test_list_tasks_has_content_hash(client):
    token = _register_and_login(client)
    r = client.get("/tasks?block=A", headers=_auth_headers(token))
    data = r.json()
    assert len(data[0]["content_hash"]) == 64  # sha256


# === version bump ===


def test_get_task_returns_db_version_not_file_version(client):
    """If DB has bumped version (force re-import), endpoint shows DB version."""
    token = _register_and_login(client, role="mentor", username="mentor3")
    from ego_server.cli import main as cli_main

    cli_main(["admin", "import-tasks", "--force"])
    r = client.get("/tasks/F1", headers=_auth_headers(token))
    assert r.status_code == 200
    data = r.json()
    assert data["version"] == "1.1.0"  # bumped


# === edge case: period in id ===


def test_get_task_specific_task_1_5(client):
    """Verify 1.5 (period in id) works."""
    token = _register_and_login(client)
    r = client.get("/tasks/1.5", headers=_auth_headers(token))
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == "1.5"
    assert data["block"] == "1"
