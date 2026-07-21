"""Tests for ego_server.sync + admin router — content-repo sync (ADR-0016).

Covers:
- :func:`ego_server.sync.sync_from_path` for both catalog and legacy layouts.
- ``POST /admin/sync-tasks`` + ``GET /admin/sync/log`` + ``GET /admin/sync/status``.
- SemVer policy (declare vs auto_minor) + breaking → stale progress.
- sync_log row written with correct counts.
"""

from __future__ import annotations

import importlib
import sqlite3
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


# === Fixtures ===


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
    """FastAPI TestClient with temp DB (no tasks imported yet)."""
    repo_root = Path(__file__).parent.parent
    monkeypatch.chdir(repo_root)

    import ego_server.main

    importlib.reload(ego_server.main)
    from ego_server.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def catalog_repo(tmp_path: Path) -> Path:
    """Build a content-repo in new (catalog) layout with 2 projects."""
    root = tmp_path / "ego-tasks"
    root.mkdir()
    (root / "catalog.yaml").write_text(
        "schema_version: 1\n"
        "projects:\n"
        "  - id: junior-core\n"
        "    path: projects/junior-core\n"
        "    enabled: true\n",
        encoding="utf-8",
    )
    proj = root / "projects" / "junior-core"
    (proj / "folders").mkdir(parents=True)
    (proj / "project.yaml").write_text(
        "id: junior-core\n"
        'name: "Junior Core"\n'
        'version: "1.0.0"\n'
        "version_policy: declare\n",
        encoding="utf-8",
    )

    # Folder F with one task.
    f = proj / "folders" / "block_f_simple"
    f.mkdir()
    (f / "folder.yaml").write_text(
        "id: block_f_simple\ncode: F\nname: 'Patterns'\nlevel: easy\n",
        encoding="utf-8",
    )
    (f / "task_f1.md").write_text(
        "---\nid: F1\ntitle: 'Test F1'\nversion: '1.0.0'\nlevel: easy\n---\n\n"
        "# Задача F1: Test\n\n## Условие\nDo the thing.\n"
        "<details><summary>Эталонное решение</summary>\n\n"
        "```python\ndef task_f1():\n    return 42\n```\n\n</details>\n",
        encoding="utf-8",
    )
    return root


@pytest.fixture
def legacy_repo(tmp_path: Path) -> Path:
    """Build a minimal legacy docs/tasks/ layout (no catalog.yaml)."""
    root = tmp_path / "docs" / "tasks"
    root.mkdir(parents=True)
    f = root / "block_f_simple"
    f.mkdir()
    (f / "task_f1.md").write_text(
        "# Задача F1: Test\n"
        "**Блок:** F — Patterns\n"
        "**Сложность:** easy\n"
        "**Темы:** find\n\n"
        "## Условие\nDo the thing.\n"
        "<details><summary>Эталонное решение</summary>\n\n"
        "```python\ndef task_f1():\n    return 42\n```\n\n</details>\n",
        encoding="utf-8",
    )
    return root


def _register_admin(client, username="admin1", password="pw"):
    r = client.post(
        "/auth/register",
        json={"username": username, "password": password, "role": "admin"},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# === sync_from_path (direct, no HTTP) ===


def test_sync_catalog_mode_inserts(temp_db, catalog_repo: Path):
    from ego_server.sync import sync_from_path

    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    try:
        result = sync_from_path(conn, catalog_repo, source="manual", repo_url=str(catalog_repo))
        conn.commit()
        assert result.added == 1
        assert result.updated == 0
        assert result.skipped == 0
        assert result.errors == 0
        assert result.status == "success"
        assert result.log_id is not None

        # projects / folders / tasks rows.
        proj = conn.execute("SELECT * FROM projects WHERE id = 'junior-core'").fetchone()
        assert proj is not None
        assert proj["name"] == "Junior Core"
        assert proj["version_policy"] == "declare"

        folder = conn.execute("SELECT * FROM folders WHERE id = 'block_f_simple'").fetchone()
        assert folder is not None
        assert folder["code"] == "F"
        assert folder["project_id"] == "junior-core"

        task = conn.execute("SELECT * FROM tasks WHERE id = 'F1'").fetchone()
        assert task is not None
        assert task["folder_id"] == "block_f_simple"
        assert task["project_id"] == "junior-core"
        assert task["version"] == "1.0.0"
    finally:
        conn.close()


def test_sync_legacy_mode_inserts(temp_db, legacy_repo: Path):
    from ego_server.sync import sync_from_path

    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    try:
        result = sync_from_path(conn, legacy_repo, source="manual", repo_url=str(legacy_repo))
        conn.commit()
        assert result.added == 1
        assert result.errors == 0

        # Legacy → synthetic fixture project.
        proj = conn.execute("SELECT * FROM projects WHERE id = 'fixture'").fetchone()
        assert proj is not None
        assert proj["version_policy"] == "auto_minor"

        task = conn.execute("SELECT * FROM tasks WHERE id = 'F1'").fetchone()
        assert task is not None
        assert task["folder_id"] == "block_f_simple"
        assert task["project_id"] == "fixture"
    finally:
        conn.close()


def test_sync_idempotent_skips(temp_db, catalog_repo: Path):
    """Second sync with unchanged content → all skipped."""
    from ego_server.sync import sync_from_path

    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    try:
        sync_from_path(conn, catalog_repo)
        conn.commit()
        result2 = sync_from_path(conn, catalog_repo)
        conn.commit()
        assert result2.added == 0
        assert result2.updated == 0
        assert result2.skipped == 1
    finally:
        conn.close()


def test_sync_declare_policy_version_not_bumped_is_error(temp_db, catalog_repo: Path):
    """declare policy: content changed but version not bumped → error."""
    from ego_server.sync import sync_from_path

    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    try:
        # First sync.
        sync_from_path(conn, catalog_repo)
        conn.commit()

        # Change content without bumping version (still 1.0.0).
        md = catalog_repo / "projects" / "junior-core" / "folders" / "block_f_simple" / "task_f1.md"
        md.write_text(
            "---\nid: F1\ntitle: 'Test F1 v2'\nversion: '1.0.0'\nlevel: easy\n---\n\n"
            "# Задача F1: Test v2\n\n## Условие\nDifferent thing.\n"
            "<details><summary>Эталонное решение</summary>\n\n"
            "```python\ndef task_f1():\n    return 99\n```\n\n</details>\n",
            encoding="utf-8",
        )
        result = sync_from_path(conn, catalog_repo)
        conn.commit()
        assert result.errors == 1
        assert result.added == 0
        assert result.updated == 0
        assert "VERSION F1" in result.error_details_text
        # 1 task, 1 error, 0 successes → failed (not partial).
        assert result.status == "failed"
    finally:
        conn.close()


def test_sync_declare_policy_version_bumped_updates(temp_db, catalog_repo: Path):
    """declare policy: content changed + version bumped → update."""
    from ego_server.sync import sync_from_path

    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    try:
        sync_from_path(conn, catalog_repo)
        conn.commit()

        md = catalog_repo / "projects" / "junior-core" / "folders" / "block_f_simple" / "task_f1.md"
        md.write_text(
            "---\nid: F1\ntitle: 'Test F1 v2'\nversion: '1.1.0'\nlevel: easy\n---\n\n"
            "# Задача F1: Test v2\n\n## Условие\nDifferent thing.\n"
            "<details><summary>Эталонное решение</summary>\n\n"
            "```python\ndef task_f1():\n    return 99\n```\n\n</details>\n",
            encoding="utf-8",
        )
        result = sync_from_path(conn, catalog_repo)
        conn.commit()
        assert result.updated == 1
        assert result.errors == 0
        task = conn.execute("SELECT version FROM tasks WHERE id = 'F1'").fetchone()
        assert task["version"] == "1.1.0"
    finally:
        conn.close()


def test_sync_auto_minor_policy_bumps_silently(temp_db, legacy_repo: Path):
    """auto_minor (legacy): content changed → silent minor bump, no error."""
    from ego_server.sync import sync_from_path

    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    try:
        sync_from_path(conn, legacy_repo)
        conn.commit()

        # Change content (no frontmatter to bump version in — auto_minor handles it).
        md = legacy_repo / "block_f_simple" / "task_f1.md"
        md.write_text(
            "# Задача F1: Test v2\n"
            "**Блок:** F — Patterns\n"
            "**Сложность:** easy\n"
            "**Темы:** find\n\n"
            "## Условие\nDifferent thing.\n"
            "<details><summary>Эталонное решение</summary>\n\n"
            "```python\ndef task_f1():\n    return 99\n```\n\n</details>\n",
            encoding="utf-8",
        )
        result = sync_from_path(conn, legacy_repo)
        conn.commit()
        assert result.updated == 1
        assert result.errors == 0
        task = conn.execute("SELECT version FROM tasks WHERE id = 'F1'").fetchone()
        assert task["version"] == "1.1.0"  # auto minor bump
    finally:
        conn.close()


def test_sync_log_row_written(temp_db, catalog_repo: Path):
    """sync_log gets a row with correct counts + status."""
    from ego_server.sync import sync_from_path

    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    try:
        sync_from_path(conn, catalog_repo, source="manual", repo_url="file://test")
        conn.commit()
        row = conn.execute("SELECT * FROM sync_log ORDER BY id DESC LIMIT 1").fetchone()
        assert row is not None
        assert row["status"] == "success"
        assert row["added"] == 1
        assert row["source"] == "manual"
        assert row["repo_url"] == "file://test"
        assert row["finished_at"] is not None
        assert row["git_sha"] is None  # PR 1: no git
    finally:
        conn.close()


# === Admin router (HTTP) ===


def test_sync_tasks_requires_admin_role(client, catalog_repo: Path):
    """Non-admin cannot trigger sync."""
    # Register as student.
    r = client.post(
        "/auth/register",
        json={"username": "student1", "password": "pw", "role": "student"},
    )
    token = r.json()["access_token"]
    r = client.post(
        "/admin/sync-tasks",
        json={"path": str(catalog_repo)},
        headers=_auth_headers(token),
    )
    assert r.status_code == 403


def test_sync_tasks_requires_auth(client):
    """No token → 401."""
    r = client.post("/admin/sync-tasks", json={"path": "/tmp"})
    assert r.status_code == 401


def test_sync_tasks_admin_success(client, catalog_repo: Path):
    token = _register_admin(client)
    r = client.post(
        "/admin/sync-tasks",
        json={"path": str(catalog_repo)},
        headers=_auth_headers(token),
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["added"] == 1
    assert data["status"] == "success"
    assert data["log_id"] > 0


def test_sync_tasks_missing_path_400(client):
    token = _register_admin(client)
    r = client.post(
        "/admin/sync-tasks",
        json={"path": "/nonexistent/path/xyz"},
        headers=_auth_headers(token),
    )
    assert r.status_code == 400
    assert "not found" in r.json()["detail"].lower()


def test_sync_tasks_file_url(client, catalog_repo: Path):
    """file:// URL is accepted."""
    token = _register_admin(client)
    r = client.post(
        "/admin/sync-tasks",
        json={"path": f"file://{catalog_repo}"},
        headers=_auth_headers(token),
    )
    assert r.status_code == 200, r.text
    assert r.json()["added"] == 1


def test_get_sync_log_empty(client):
    token = _register_admin(client)
    r = client.get("/admin/sync/log", headers=_auth_headers(token))
    assert r.status_code == 200
    assert r.json() == []


def test_get_sync_log_after_sync(client, catalog_repo: Path):
    token = _register_admin(client)
    client.post(
        "/admin/sync-tasks",
        json={"path": str(catalog_repo)},
        headers=_auth_headers(token),
    )
    r = client.get("/admin/sync/log", headers=_auth_headers(token))
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["status"] == "success"
    assert data[0]["added"] == 1


def test_get_sync_status(client, catalog_repo: Path):
    token = _register_admin(client)
    # Before sync: null.
    r = client.get("/admin/sync/status", headers=_auth_headers(token))
    assert r.status_code == 200
    assert r.json() is None
    # After sync.
    client.post(
        "/admin/sync-tasks",
        json={"path": str(catalog_repo)},
        headers=_auth_headers(token),
    )
    r = client.get("/admin/sync/status", headers=_auth_headers(token))
    assert r.status_code == 200
    assert r.json()["status"] == "success"


def test_sync_log_mentor_can_read(client, catalog_repo: Path):
    """Mentor role can read sync_log (read-only ops view)."""
    # Admin syncs.
    admin_token = _register_admin(client, "admin_a")
    client.post(
        "/admin/sync-tasks",
        json={"path": str(catalog_repo)},
        headers=_auth_headers(admin_token),
    )
    # Mentor reads.
    r = client.post(
        "/auth/register",
        json={"username": "mentor1", "password": "pw", "role": "mentor"},
    )
    mentor_token = r.json()["access_token"]
    r = client.get("/admin/sync/log", headers=_auth_headers(mentor_token))
    assert r.status_code == 200
    assert len(r.json()) == 1


# === CLI ===


def test_cli_sync_tasks_success(temp_db, catalog_repo: Path):
    from ego_server.cli import main as cli_main

    rc = cli_main(["admin", "sync-tasks", "--from", str(catalog_repo)])
    assert rc == 0
    conn = sqlite3.connect(temp_db)
    try:
        row = conn.execute("SELECT added, status FROM sync_log ORDER BY id DESC LIMIT 1").fetchone()
        assert row[0] == 1
        assert row[1] == "success"
    finally:
        conn.close()


def test_cli_sync_tasks_missing_path(temp_db):
    from ego_server.cli import main as cli_main

    rc = cli_main(["admin", "sync-tasks", "--from", "/nonexistent/xyz"])
    assert rc == 1


def test_cli_sync_tasks_help_lists_command():
    from ego_server.cli import main as cli_main
    from io import StringIO
    import sys

    old_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        try:
            cli_main(["admin", "--help"])
        except SystemExit as e:
            assert e.code == 0
        out = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout
    assert "sync-tasks" in out
