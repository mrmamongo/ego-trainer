"""Tests for `ego pull` (beads ego-trainer-8bv.4)."""

from __future__ import annotations

import importlib
import json
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ego.cli.main import main


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
def server_client(temp_db, monkeypatch):
    """FastAPI TestClient with 33 tasks imported, running on a real port."""
    repo_root = Path(__file__).parent.parent
    monkeypatch.chdir(repo_root)

    import ego_server.main

    importlib.reload(ego_server.main)
    from ego_server.main import app

    from ego_server.cli import main as cli_main

    cli_main(["admin", "import-tasks", "--docs-dir", "docs/tasks"])

    with TestClient(app) as c:
        yield c


@pytest.fixture
def ego_with_token(tmp_path, monkeypatch, server_client):
    """Create .ego/ with config pointing to the test server."""
    monkeypatch.chdir(tmp_path)

    # Register a student and get token.
    r = server_client.post(
        "/auth/register",
        json={"username": "pulluser", "password": "pw", "role": "student"},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]

    # Get the actual server URL from the test client.
    # TestClient uses http://testserver internally — we need to use it directly.
    # For pull, we'll mock the HTTP calls using the TestClient.
    ego = tmp_path / ".ego"
    ego.mkdir()
    config = {
        "server_url": "http://testserver",
        "token": token,
        "student_id": r.json()["user_id"],
        "student_username": "pulluser",
        "role": "student",
        "sandbox_timeout_sec": 5.0,
        "sandbox_block_network": True,
        "log_truncate_to": 8192,
    }
    (ego / "config.yaml").write_text(json.dumps(config), encoding="utf-8")
    (ego / "manifest.yaml").write_text(
        json.dumps({"tasks": [], "server_version": "", "last_pull_at": None}),
        encoding="utf-8",
    )
    (ego / "progress.json").write_text(
        json.dumps({"student_username": "pulluser", "entries": []}),
        encoding="utf-8",
    )
    (ego / "runs").mkdir()
    (ego / "cache" / "sol").mkdir(parents=True)

    return tmp_path, server_client, token


def _patch_urlopen(monkeypatch, client, token):
    """Patch urllib.request.urlopen to use the TestClient instead."""
    import urllib.request

    class FakeResponse:
        def __init__(self, data: bytes):
            self._data = data
            self._pos = 0

        def read(self) -> bytes:
            return self._data

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    def fake_urlopen(req, timeout=None):
        url = req.full_url
        method = req.get_method()
        headers = dict(req.headers)
        # Map URL to TestClient call.
        path = url.replace("http://testserver", "")
        if method == "GET":
            r = client.get(path, headers=headers)
        else:
            raise ValueError(f"Unexpected method: {method}")
        if r.status_code != 200:
            import urllib.error

            raise urllib.error.HTTPError(
                url, r.status_code, r.reason_phrase, {}, None
            )
        return FakeResponse(r.content)

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)


# === basic ===


def test_pull_no_ego_dir(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    rc = main(["pull", "--all"])
    assert rc == 1
    captured = capsys.readouterr()
    assert ".ego/" in captured.err


def test_pull_no_filter(ego_with_token, monkeypatch, capsys):
    tmp_path, client, token = ego_with_token
    _patch_urlopen(monkeypatch, client, token)
    rc = main(["pull"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "Specify" in captured.err


def test_pull_all(ego_with_token, monkeypatch, capsys):
    tmp_path, client, token = ego_with_token
    _patch_urlopen(monkeypatch, client, token)
    rc = main(["pull", "--all"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Pulled: 33" in captured.out
    # Check files were created.
    tasks_dir = tmp_path / "tasks"
    assert tasks_dir.exists()
    # At least one .md and .py.
    md_files = list(tasks_dir.rglob("*.md"))
    py_files = list(tasks_dir.rglob("*.py"))
    assert len(md_files) == 33
    assert len(py_files) == 33
    # Cache.
    sol_files = list((tmp_path / ".ego" / "cache" / "sol").glob("*.py"))
    assert len(sol_files) == 33
    cond_files = list((tmp_path / ".ego" / "cache" / "cond").glob("*.md"))
    assert len(cond_files) == 33
    # Manifest.
    manifest = json.loads((tmp_path / ".ego" / "manifest.yaml").read_text("utf-8"))
    assert len(manifest["tasks"]) == 33


def test_pull_block_filter(ego_with_token, monkeypatch, capsys):
    tmp_path, client, token = ego_with_token
    _patch_urlopen(monkeypatch, client, token)
    rc = main(["pull", "--block", "F"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Pulled: 5" in captured.out  # F1-F5
    # Only F block tasks.
    md_files = list((tmp_path / "tasks").rglob("*.md"))
    assert len(md_files) == 5


def test_pull_task_filter(ego_with_token, monkeypatch, capsys):
    tmp_path, client, token = ego_with_token
    _patch_urlopen(monkeypatch, client, token)
    rc = main(["pull", "--task", "F1"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Pulled: 1" in captured.out
    # Only F1.
    md_files = list((tmp_path / "tasks").rglob("*.md"))
    assert len(md_files) == 1
    assert "task_f1" in str(md_files[0])


def test_pull_writes_stub_py(ego_with_token, monkeypatch, capsys):
    """Stub .py should contain the task function signature with pass."""
    tmp_path, client, token = ego_with_token
    _patch_urlopen(monkeypatch, client, token)
    main(["pull", "--task", "F1"])
    py_files = list((tmp_path / "tasks").rglob("task_f1.py"))
    assert len(py_files) == 1
    content = py_files[0].read_text("utf-8")
    assert "def task_f1_find_critical" in content
    assert "pass" in content


def test_pull_writes_manifest(ego_with_token, monkeypatch, capsys):
    """Manifest should have entries with correct metadata."""
    tmp_path, client, token = ego_with_token
    _patch_urlopen(monkeypatch, client, token)
    main(["pull", "--task", "F1"])
    manifest = json.loads((tmp_path / ".ego" / "manifest.yaml").read_text("utf-8"))
    assert len(manifest["tasks"]) == 1
    entry = manifest["tasks"][0]
    assert entry["id"] == "F1"
    assert entry["block"] == "F"
    assert entry["version"] == "1.0.0"
    assert entry["content_hash"]
    assert entry["pulled_at"]


def test_pull_no_matching_tasks(ego_with_token, monkeypatch, capsys):
    tmp_path, client, token = ego_with_token
    _patch_urlopen(monkeypatch, client, token)
    rc = main(["pull", "--block", "ZZZ"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "No tasks matched" in captured.err


def test_pull_help(capsys):
    with pytest.raises(SystemExit):
        main(["pull", "--help"])
    captured = capsys.readouterr()
    assert "--block" in captured.out
    assert "--task" in captured.out
    assert "--all" in captured.out
