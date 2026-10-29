"""Challenge folders through content-repo sync (ADR-0018 D18.1, D18.6 core).

The fixture catalog ``tests/fixtures/challenges_catalog`` has one
``kind: challenge`` folder with two stages: sync must store the folder as
``challenge`` with its workspace JSON, and the stages as ordinary ``tasks``
rows with ``challenge_stage`` 1 and 2 (no extra table).
"""

from __future__ import annotations

import importlib
import json
import sqlite3
import tempfile
from pathlib import Path

import pytest

FIXTURE_CATALOG = Path(__file__).parent / "fixtures" / "challenges_catalog"


@pytest.fixture
def temp_db(monkeypatch):
    """Fresh temp SQLite DB with schema applied."""
    tmp = Path(tempfile.mkdtemp()) / "test.db"
    monkeypatch.setenv("EGO_DB_PATH", str(tmp))

    import ego_server.config
    import ego_server.db

    importlib.reload(ego_server.config)
    importlib.reload(ego_server.db)
    ego_server.db.init_db()
    yield tmp


def _sync(path: Path) -> sqlite3.Connection:
    from ego_server.sync import sync_from_path

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    result = sync_from_path(conn, FIXTURE_CATALOG, source="manual", repo_url=str(path))
    conn.commit()
    assert result.errors == 0, result.error_details
    return conn


def test_challenge_stages_are_synced_as_tasks(temp_db):
    conn = _sync(temp_db)
    try:
        rows = conn.execute(
            "SELECT id, title, level, challenge_stage FROM tasks ORDER BY challenge_stage"
        ).fetchall()
        assert [row["id"] for row in rows] == ["KV01", "KV02"]
        assert [row["challenge_stage"] for row in rows] == [1, 2]
        assert rows[0]["title"] == "Разбор команды"
        assert rows[0]["level"] == "easy"
        assert rows[1]["level"] == "medium"
    finally:
        conn.close()


def test_challenge_folder_keeps_kind_and_workspace(temp_db):
    conn = _sync(temp_db)
    try:
        folder = conn.execute("SELECT id, kind, workspace_json FROM folders").fetchone()
        assert folder["kind"] == "challenge"
        workspace = json.loads(folder["workspace_json"])
        assert workspace["entry"] == "main.py"
        assert workspace["include"] == ["*.py", "data/*.json"]
    finally:
        conn.close()


def test_ordinary_folder_is_tasks_with_null_workspace(temp_db):
    """A folder without ``kind`` keeps the default and no workspace JSON."""
    from ego.catalog import parse_folder

    folder = parse_folder("id: block_f_simple\ncode: F\nname: Patterns\n")
    assert folder.kind == "tasks"
    assert folder.workspace is None
    assert not folder.is_challenge
