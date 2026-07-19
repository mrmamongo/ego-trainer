"""Tests for ``ego_server.cli`` — run/migrate/admin commands.

The ``run`` command (which starts uvicorn) is intentionally not tested here.
These tests cover ``migrate`` and the ``admin`` subcommands against a temp
SQLite database.

Note on parallel work: ``ego_server.auth`` (task bmh.2 / Server.2) may not
exist yet when these tests run. ``ego_server.cli._load_auth`` falls back to a
local uuid4 + sha256 implementation in that case, so ``create-user`` keeps
working. Once ``ego_server.auth`` lands the real (bcrypt) implementation is
used automatically — these tests do not assert on the hash format.
"""

from __future__ import annotations

import importlib
import sqlite3
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_db(monkeypatch):
    """Yield a path to a fresh temp DB with the schema already applied.

    Sets ``EGO_DB_PATH``, reloads ``ego_server.config`` and ``ego_server.db``
    so the already-imported modules pick up the new path, then runs
    ``init_db()`` so every admin command has the tables it needs.
    """
    tmp = Path(tempfile.mkdtemp()) / "test.db"
    monkeypatch.setenv("EGO_DB_PATH", str(tmp))

    import ego_server.config
    import ego_server.db

    importlib.reload(ego_server.config)
    importlib.reload(ego_server.db)

    from ego_server.db import init_db

    init_db()
    yield tmp


# === help / version ===


def test_help_returns_0(capsys):
    from ego_server.cli import main

    rc = main([])
    assert rc == 0
    captured = capsys.readouterr()
    assert "ego-server" in captured.out
    assert "run" in captured.out
    assert "migrate" in captured.out
    assert "admin" in captured.out


def test_version(capsys):
    from ego_server.cli import main

    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "ego-server" in captured.out


# === migrate ===


def test_migrate_creates_tables(temp_db):
    from ego_server.cli import main

    rc = main(["migrate"])
    assert rc == 0
    conn = sqlite3.connect(temp_db)
    tables = [
        r[0]
        for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    ]
    assert "tasks" in tables
    assert "students" in tables
    assert "progress" in tables
    assert "runs" in tables
    assert "task_versions" in tables


# === admin create-user ===


def test_create_user(temp_db):
    from ego_server.cli import main

    rc = main(
        ["admin", "create-user", "--username", "alice", "--password", "pw123",
         "--role", "mentor"]
    )
    assert rc == 0
    conn = sqlite3.connect(temp_db)
    row = conn.execute(
        "SELECT username, role FROM students WHERE username = 'alice'"
    ).fetchone()
    assert row
    assert row[1] == "mentor"


def test_create_user_default_role(temp_db):
    from ego_server.cli import main

    rc = main(["admin", "create-user", "--username", "carol", "--password", "pw"])
    assert rc == 0
    conn = sqlite3.connect(temp_db)
    row = conn.execute(
        "SELECT role FROM students WHERE username = 'carol'"
    ).fetchone()
    assert row
    assert row[0] == "student"


def test_create_user_duplicate_fails(temp_db, capsys):
    from ego_server.cli import main

    main(["admin", "create-user", "--username", "bob", "--password", "pw"])
    capsys.readouterr()  # clear first output
    rc = main(["admin", "create-user", "--username", "bob", "--password", "pw2"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "already exists" in captured.err


# === admin list-users ===


def test_list_users_empty(temp_db, capsys):
    from ego_server.cli import main

    rc = main(["admin", "list-users"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "no users" in captured.out


def test_list_users_with_data(temp_db, capsys):
    from ego_server.cli import main

    main(["admin", "create-user", "--username", "alice", "--password", "p"])
    main(
        ["admin", "create-user", "--username", "bob", "--password", "p",
         "--role", "mentor"]
    )
    capsys.readouterr()  # clear create-user output
    rc = main(["admin", "list-users"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "alice" in captured.out
    assert "bob" in captured.out
    assert "2 users" in captured.out


# === admin import-tasks ===


def test_import_tasks(temp_db, capsys, monkeypatch):
    """import-tasks should import .md from docs/tasks/ into DB."""
    from ego_server.cli import main

    # Run from repo root so docs/tasks/ resolves.
    monkeypatch.chdir(Path(__file__).parent.parent)
    rc = main(["admin", "import-tasks", "--docs-dir", "docs/tasks"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Imported: 33" in captured.out
    conn = sqlite3.connect(temp_db)
    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    assert count == 33
    # Check a specific task.
    row = conn.execute(
        "SELECT title, level, version FROM tasks WHERE id = 'F1'"
    ).fetchone()
    assert row
    assert "Найди" in row[0]  # title starts with "Найди первый критический баг"
    assert row[1] == "easy"
    assert row[2] == "1.0.0"
    # Version history should have one row per task.
    versions = conn.execute("SELECT COUNT(*) FROM task_versions").fetchone()[0]
    assert versions == 33


def test_import_tasks_idempotent(temp_db, capsys, monkeypatch):
    """Running import-tasks twice should skip all (content unchanged)."""
    from ego_server.cli import main

    monkeypatch.chdir(Path(__file__).parent.parent)
    main(["admin", "import-tasks", "--docs-dir", "docs/tasks"])
    capsys.readouterr()  # clear
    rc = main(["admin", "import-tasks", "--docs-dir", "docs/tasks"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Skipped: 33" in captured.out
    assert "Imported: 0" in captured.out


def test_import_tasks_force_updates(temp_db, capsys, monkeypatch):
    """--force re-imports even if content_hash matches (minor version bump)."""
    from ego_server.cli import main

    monkeypatch.chdir(Path(__file__).parent.parent)
    main(["admin", "import-tasks", "--docs-dir", "docs/tasks"])
    capsys.readouterr()
    rc = main(["admin", "import-tasks", "--docs-dir", "docs/tasks", "--force"])
    assert rc == 0
    captured = capsys.readouterr()
    # All 33 should be updated.
    assert "Updated: 33" in captured.out
    assert "Imported: 0" in captured.out


def test_import_tasks_bumps_minor_version(temp_db, monkeypatch):
    """When content changes (force), minor version bumps 1.0.0 -> 1.1.0."""
    from ego_server.cli import main

    monkeypatch.chdir(Path(__file__).parent.parent)
    main(["admin", "import-tasks", "--docs-dir", "docs/tasks"])
    conn = sqlite3.connect(temp_db)
    v1 = conn.execute(
        "SELECT version FROM tasks WHERE id = 'F1'"
    ).fetchone()[0]
    assert v1 == "1.0.0"
    # Re-import with force -> version bump.
    main(["admin", "import-tasks", "--docs-dir", "docs/tasks", "--force"])
    v2 = conn.execute(
        "SELECT version FROM tasks WHERE id = 'F1'"
    ).fetchone()[0]
    assert v2 == "1.1.0"
    # task_versions should now have two rows for F1.
    n = conn.execute(
        "SELECT COUNT(*) FROM task_versions WHERE task_id = 'F1'"
    ).fetchone()[0]
    assert n == 2


def test_import_tasks_missing_dir(temp_db, capsys, monkeypatch):
    """import-tasks on a non-existent dir returns 1."""
    from ego_server.cli import main

    monkeypatch.chdir(Path(__file__).parent.parent)
    rc = main(["admin", "import-tasks", "--docs-dir", "does/not/exist"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "not found" in captured.err


# === admin help ===


def test_admin_no_subcommand_prints_help(capsys):
    from ego_server.cli import main

    rc = main(["admin"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "create-user" in captured.out or "import-tasks" in captured.out
