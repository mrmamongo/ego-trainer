"""Tests for GET /tasks/<id>/hints — progressive hints (ADR-0014)."""

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


# === GET /tasks/<id>/hints ===


def test_hints_requires_auth(client):
    r = client.get("/tasks/F1/hints")
    assert r.status_code == 401


def test_hints_task_not_found(client):
    token, _ = _register_and_login(client)
    r = client.get("/tasks/ZZZ/hints", headers=_auth_headers(token))
    assert r.status_code == 404


def test_hints_returns_all_levels(client):
    token, _ = _register_and_login(client)
    r = client.get("/tasks/F1/hints", headers=_auth_headers(token))
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["task_id"] == "F1"
    assert len(data["hints"]) >= 1
    # Should have levels 1, 2, 3.
    levels = [h["level"] for h in data["hints"]]
    assert 1 in levels  # Rules
    assert 2 in levels  # Example
    assert 3 in levels  # Signature


def test_hints_level_1_only(client):
    """?level=1 should return only rules."""
    token, _ = _register_and_login(client)
    r = client.get("/tasks/F1/hints?level=1", headers=_auth_headers(token))
    assert r.status_code == 200
    data = r.json()
    levels = [h["level"] for h in data["hints"]]
    assert all(l <= 1 for l in levels)
    assert 1 in levels


def test_hints_level_2(client):
    """?level=2 should return rules + example."""
    token, _ = _register_and_login(client)
    r = client.get("/tasks/F1/hints?level=2", headers=_auth_headers(token))
    assert r.status_code == 200
    data = r.json()
    levels = [h["level"] for h in data["hints"]]
    assert all(l <= 2 for l in levels)


def test_hints_level_3_has_signature(client):
    """Level 3 hint should contain function signature."""
    token, _ = _register_and_login(client)
    r = client.get("/tasks/F1/hints?level=3", headers=_auth_headers(token))
    assert r.status_code == 200
    data = r.json()
    sig_hints = [h for h in data["hints"] if h["level"] == 3]
    assert len(sig_hints) == 1
    assert "def task_" in sig_hints[0]["content"]


def test_hints_level_1_has_rules(client):
    """Level 1 hint should contain rules text."""
    token, _ = _register_and_login(client)
    r = client.get("/tasks/F1/hints?level=1", headers=_auth_headers(token))
    assert r.status_code == 200
    data = r.json()
    rules_hints = [h for h in data["hints"] if h["level"] == 1]
    assert len(rules_hints) == 1
    assert rules_hints[0]["title"] == "Правила"
    # F1 rules mention "critical" or "severity".
    assert "critical" in rules_hints[0]["content"].lower() or "severity" in rules_hints[0]["content"].lower()


def test_hints_level_2_has_example(client):
    """Level 2 hint should contain example code."""
    token, _ = _register_and_login(client)
    r = client.get("/tasks/F1/hints?level=2", headers=_auth_headers(token))
    assert r.status_code == 200
    data = r.json()
    example_hints = [h for h in data["hints"] if h["level"] == 2]
    assert len(example_hints) == 1
    assert example_hints[0]["title"] == "Пример"
    # Example should contain python code or function call.
    assert "task_f1" in example_hints[0]["content"] or "bugs" in example_hints[0]["content"].lower()
