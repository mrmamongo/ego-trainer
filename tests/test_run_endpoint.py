"""POST /run — sandbox execution for the IDE Run button."""

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
def client(temp_db):
    import ego_server.main

    importlib.reload(ego_server.main)
    from ego_server.main import app

    with TestClient(app) as c:
        yield c


def _token(client: TestClient) -> str:
    import uuid

    r = client.post(
        "/auth/register",
        json={"username": f"run_{uuid.uuid4().hex[:8]}", "password": "pw-run-1"},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def test_run_requires_auth(client: TestClient):
    r = client.post("/run", json={"code": "print(1)"})
    assert r.status_code == 401


def test_run_prints_stdout(client: TestClient):
    token = _token(client)
    r = client.post(
        "/run",
        json={"code": "print('hello')\nprint(2 + 2)"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert "hello" in body["stdout"]
    assert "4" in body["stdout"]
    assert body["returncode"] == 0
    assert not body["timed_out"]


def test_run_returns_stderr_on_exception(client: TestClient):
    token = _token(client)
    r = client.post(
        "/run",
        json={"code": "raise ValueError('boom')"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["returncode"] == 1
    assert "ValueError" in body["stderr"]
    assert "boom" in body["stderr"]


def test_run_timeout(client: TestClient):
    token = _token(client)
    r = client.post(
        "/run",
        json={"code": "while True:\n    pass"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["timed_out"] is True


def test_run_size_limit(client: TestClient, monkeypatch):
    # Default max_code_chars (100000) — send bigger.
    token = _token(client)
    r = client.post(
        "/run",
        json={"code": "x = 1\n" + "#" * 200_000},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 413
