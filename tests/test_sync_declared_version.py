"""Regress declared-version sync when only tests change and Studio saves a bump."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from tests.test_server_admin import (
    _auth_headers,
    _create_user,
    _db_task_row,
    _db_task_versions,
    _get_studio_etag,
    _read_canonical,
    _save_payload,
    _valid_candidate_md,
    studio_env as _studio_env_fixture,  # noqa: F401 - shared catalog + isolated TestClient fixture
)
from tests.test_server_sync import temp_db as _temp_db_fixture  # noqa: F401 - shared isolated schema fixture


studio_env = _studio_env_fixture

temp_db = _temp_db_fixture


def _write_repo(root: Path, *, version: str = "1.0.0", breaking: bool = False) -> Path:
    folder = root / "projects" / "training" / "folders" / "basics"
    folder.mkdir(parents=True)
    (root / "catalog.yaml").write_text(
        "schema_version: 1\nprojects:\n  - id: training\n    path: projects/training\n",
        encoding="utf-8",
    )
    (folder.parent.parent / "project.yaml").write_text(
        "id: training\nname: Training\nversion: '1.0.0'\nversion_policy: declare\n",
        encoding="utf-8",
    )
    (folder / "folder.yaml").write_text(
        "id: basics\ncode: B\nname: Basics\nlevel: easy\n",
        encoding="utf-8",
    )
    (folder / "task_b1.md").write_text(
        f"---\nid: B1\ntitle: First failed build\nversion: '{version}'\n"
        f"level: easy\nfolder: basics\nbreaking: {str(breaking).lower()}\n---\n\n"
        "# Задача B1: First failed build\n\n## Условие\n\nReturn the first failed build id, or an empty string.\n",
        encoding="utf-8",
    )
    (folder / "task_b1.solution.py").write_text(
        "def task_b1_first_failed_build(builds):\n"
        "    for build in builds:\n"
        "        if build['status'] == 'failed':\n"
        "            return build['id']\n"
        "    return ''\n",
        encoding="utf-8",
    )
    (folder / "task_b1.tests.py").write_text(
        "from ego.testing import case\n\n"
        "@case(args=([{'id': 'build-1', 'status': 'failed'}],), "
        "expected='build-1', description='first failed build', level='smoke')\n"
        "def task_b1_first_failed_build(builds):\n    ...\n",
        encoding="utf-8",
    )
    return root


def _sync(database: Path, repo: Path):
    from ego_server.sync import sync_from_path

    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    try:
        result = sync_from_path(connection, repo)
        connection.commit()
        return result
    finally:
        connection.close()


def test_tests_only_edit_with_declared_version_bump_updates_and_marks_breaking_stale(
    temp_db: Path, tmp_path: Path
) -> None:
    from ego_server.db import get_connection

    repo = _write_repo(tmp_path / "content")
    first = _sync(temp_db, repo)
    assert first.added == 1
    assert first.errors == 0

    connection = get_connection()
    try:
        before = connection.execute(
            "SELECT version,content_hash FROM tasks WHERE id='B1'"
        ).fetchone()
        assert before["version"] == "1.0.0"
        connection.execute(
            "INSERT INTO progress "
            "(student_id,task_id,version,status,attempts,passed_tests,total_tests,last_run_at) "
            "VALUES ('qa-student','B1','1.0.0','passed',1,1,1,datetime('now'))"
        )
        connection.commit()
    finally:
        connection.close()

    task_dir = repo / "projects" / "training" / "folders" / "basics"
    md_path = task_dir / "task_b1.md"
    markdown = md_path.read_text(encoding="utf-8")
    md_path.write_text(
        markdown.replace("version: '1.0.0'", "version: '1.1.0'").replace(
            "breaking: false", "breaking: true"
        ),
        encoding="utf-8",
    )
    tests_path = task_dir / "task_b1.tests.py"
    tests_path.write_text(
        tests_path.read_text(encoding="utf-8")
        + "\n@case(args=([],), expected='', description='empty input', level='smoke')\n"
        + "def task_b1_empty(builds):\n    ...\n",
        encoding="utf-8",
    )

    second = _sync(temp_db, repo)
    assert second.updated == 1
    assert second.errors == 0

    connection = get_connection()
    try:
        task = connection.execute(
            "SELECT version,content_hash,breaking FROM tasks WHERE id='B1'"
        ).fetchone()
        versions = connection.execute(
            "SELECT version,content_hash,breaking FROM task_versions "
            "WHERE task_id='B1' ORDER BY version"
        ).fetchall()
        progress = connection.execute(
            "SELECT status FROM progress WHERE student_id='qa-student' AND task_id='B1'"
        ).fetchone()
        assert task["version"] == "1.1.0"
        assert task["content_hash"] == before["content_hash"]
        assert task["breaking"] == 1
        assert [row["version"] for row in versions] == ["1.0.0", "1.1.0"]
        assert versions[-1]["content_hash"] == before["content_hash"]
        assert versions[-1]["breaking"] == 1
        assert progress["status"] == "stale"
    finally:
        connection.close()


def test_tests_only_edit_with_lower_declared_version_remains_an_error(
    temp_db: Path, tmp_path: Path
) -> None:
    repo = _write_repo(tmp_path / "content")
    first = _sync(temp_db, repo)
    assert first.added == 1

    task_dir = repo / "projects" / "training" / "folders" / "basics"
    md_path = task_dir / "task_b1.md"
    markdown = md_path.read_text(encoding="utf-8")
    md_path.write_text(markdown.replace("version: '1.0.0'", "version: '0.9.0'"), encoding="utf-8")
    tests_path = task_dir / "task_b1.tests.py"
    tests_path.write_text(
        tests_path.read_text(encoding="utf-8") + "\n# tests-only edit\n", encoding="utf-8"
    )

    result = _sync(temp_db, repo)
    assert result.errors == 1
    assert result.updated == 0
    assert "VERSION B1" in result.error_details_text

    connection = sqlite3.connect(temp_db)
    try:
        assert (
            connection.execute("SELECT version FROM tasks WHERE id='B1'").fetchone()[0] == "1.0.0"
        )
    finally:
        connection.close()


def test_task_studio_saves_tests_only_edit_with_declared_version_bump(
    studio_env: TestClient,
) -> None:
    admin_token, _ = _create_user(studio_env, "sync-version-admin", "pw", "admin")
    # Replace the browse fixture's placeholder hash with an actual initial sync.
    from ego_server.content_config import content_settings
    from ego_server.db import get_connection
    from ego_server.sync import sync_from_path

    connection = get_connection()
    try:
        connection.execute("DELETE FROM tasks WHERE id='F1'")
        initial = sync_from_path(connection, content_settings.to_config().resolved_local_path)
        assert initial.errors == 0
        connection.commit()
    finally:
        connection.close()
    etag = _get_studio_etag(studio_env, admin_token)
    canonical_before = _read_canonical(studio_env)
    row_before = _db_task_row()
    versions_before = _db_task_versions()

    # Seed prior progress so breaking metadata must stale it during Studio's re-sync.

    connection = get_connection()
    try:
        connection.execute(
            "INSERT INTO progress "
            "(student_id,task_id,version,status,attempts,passed_tests,total_tests,last_run_at) "
            "VALUES ('studio-qa-student','F1','1.0.0','passed',1,1,1,datetime('now'))"
        )
        connection.commit()
    finally:
        connection.close()

    candidate_md = _valid_candidate_md(version="1.1.0").replace(
        "level: easy", "level: easy\nbreaking: true"
    )
    candidate_tests = canonical_before["task_f1.tests.py"] + "\n# added edge-case coverage\n"
    response = studio_env.put(
        "/admin/tasks/F1/studio",
        json=_save_payload(
            expected_version="1.0.0",
            expected_content_etag=etag,
            markdown=candidate_md,
            solution_py=canonical_before["task_f1.solution.py"],
            tests_py=candidate_tests,
        ),
        headers=_auth_headers(admin_token),
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["new_version"] == "1.1.0"
    assert payload["sync"]["updated"] == 1
    assert payload["sync"]["errors"] == 0

    canonical_after = _read_canonical(studio_env)
    assert canonical_after["task_f1.solution.py"] == canonical_before["task_f1.solution.py"]
    assert canonical_after["task_f1.tests.py"] != canonical_before["task_f1.tests.py"]
    row_after = _db_task_row()
    assert row_after["version"] == "1.1.0"
    assert row_after["content_hash"] == row_before["content_hash"]
    versions_after = _db_task_versions()
    assert len(versions_after) == len(versions_before) + 1
    assert versions_after[-1]["version"] == "1.1.0"

    connection = get_connection()
    try:
        progress = connection.execute(
            "SELECT status FROM progress WHERE student_id='studio-qa-student' AND task_id='F1'"
        ).fetchone()
        assert progress["status"] == "stale"
    finally:
        connection.close()
