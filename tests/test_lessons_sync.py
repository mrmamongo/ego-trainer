"""Tests for theory cards in sync + schema migration to the lessons table.

Covers:
- schema migration on a DB created from the pre-lessons ``schema.sql``;
- lesson upsert (add / update / delete) driven by ``lesson_*.md``;
- task ``theory`` refresh without a version bump, unknown-id warnings,
  duplicate lesson ids as sync errors.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from ego_server.db import SCHEMA_PATH, init_schema
from ego_server.sync import sync_from_path


# === Helpers ===


def _connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _old_schema_sql() -> str:
    """Current schema.sql minus the theory-cards additions."""
    kept: list[str] = []
    skip_lessons = False
    for line in SCHEMA_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("-- Теория"):
            skip_lessons = True
            continue
        if skip_lessons:
            if stripped == ");":
                skip_lessons = False
            continue
        if "idx_lessons_" in stripped or stripped.startswith("theory "):
            continue
        kept.append(line)
    return "\n".join(kept)


_TASK_MD = """---
id: F1
title: 'Test F1'
version: '{version}'
level: easy
{theory_line}---

# Задача F1: Test

## Условие
Do the thing.

<details><summary>Эталонное решение</summary>

```python
def task_f1():
    return 42
```

</details>
"""

_TASK_MD_V2 = """---
id: F1
title: 'Test F1 v2'
version: '{version}'
level: easy
{theory_line}---

# Задача F1: Test v2

## Условие
Do a different thing.

<details><summary>Эталонное решение</summary>

```python
def task_f1():
    return 99
```

</details>
"""


def _write_task(folder: Path, *, version: str = "1.0.0", theory: list[str] | None = None,
                template: str = _TASK_MD) -> None:
    theory_line = f"theory: [{', '.join(theory)}]\n" if theory is not None else ""
    folder.joinpath("task_f1.md").write_text(
        template.format(version=version, theory_line=theory_line), encoding="utf-8"
    )


def _write_lesson(folder: Path, slug: str, *, lesson_id: str, order: int = 0,
                  body: str = "Text.", version: str = "1.0.0") -> Path:
    path = folder / f"lesson_{slug}.md"
    path.write_text(
        f"---\nid: {lesson_id}\ntitle: 'Урок {lesson_id}'\norder: {order}\n"
        f"version: '{version}'\n---\n\n# Урок {lesson_id}\n\n{body}\n",
        encoding="utf-8",
    )
    return path


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """One-project catalog repo with a folder holding one task + one lesson."""
    root = tmp_path / "ego-tasks"
    folder = root / "projects" / "junior-core" / "folders" / "block_f_simple"
    folder.mkdir(parents=True)
    (root / "catalog.yaml").write_text(
        "schema_version: 1\nprojects:\n  - id: junior-core\n"
        "    path: projects/junior-core\n    enabled: true\n",
        encoding="utf-8",
    )
    (folder.parent.parent / "project.yaml").write_text(
        'id: junior-core\nname: "Junior Core"\nversion: "1.0.0"\nversion_policy: declare\n',
        encoding="utf-8",
    )
    (folder / "folder.yaml").write_text(
        "id: block_f_simple\ncode: F\nname: 'Patterns'\nlevel: easy\n", encoding="utf-8"
    )
    _write_task(folder, theory=["roles"])
    _write_lesson(folder, "roles", lesson_id="roles", order=1)
    return root


def _folder_of(repo: Path) -> Path:
    return repo / "projects" / "junior-core" / "folders" / "block_f_simple"


@pytest.fixture
def temp_db(monkeypatch, tmp_path: Path):
    from ego_server.config import settings

    monkeypatch.setattr(settings, "db_path", tmp_path / "test.db")
    init_schema(_connect(settings.db_path))
    return settings.db_path


def _lesson_ids(conn: sqlite3.Connection) -> list[str]:
    return [row["id"] for row in conn.execute("SELECT id FROM lessons ORDER BY id")]


# === Migration ===


def test_old_schema_migrates_to_lessons_and_theory(tmp_path: Path):
    conn = _connect(tmp_path / "old.sqlite")
    try:
        conn.executescript(_old_schema_sql())
        conn.execute(
            "INSERT INTO tasks (id, block, slug, task_id, title, level, version, "
            "content_hash, md_path, created_at, updated_at) "
            "VALUES ('OLD1', 'OLD', 'block_old', 'OLD1', 'Old', 'easy', '1.0.0', 'h', 'p', "
            "'2026-01-01', '2026-01-01')"
        )
        conn.commit()
        task_cols = {row["name"] for row in conn.execute("PRAGMA table_info(tasks)")}
        tables = {
            row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        assert "theory" not in task_cols
        assert "lessons" not in tables

        init_schema(conn)
        init_schema(conn)  # idempotent

        task_cols = {row["name"] for row in conn.execute("PRAGMA table_info(tasks)")}
        tables = {
            row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        assert "theory" in task_cols
        assert "lessons" in tables
        lesson_cols = {row["name"] for row in conn.execute("PRAGMA table_info(lessons)")}
        assert lesson_cols == {
            "id",
            "project_id",
            "folder_id",
            "title",
            "order",
            "version",
            "content_hash",
            "body_md",
            "created_at",
            "updated_at",
        }
        # Existing rows survive with empty theory.
        row = conn.execute("SELECT theory FROM tasks WHERE id = 'OLD1'").fetchone()
        assert row["theory"] == "[]"
    finally:
        conn.close()


def test_migration_runs_even_without_schema_sql(tmp_path: Path):
    """``_migrate_add_columns`` alone creates the lessons table (old DB copy)."""
    from ego_server.db import _migrate_add_columns

    conn = _connect(tmp_path / "bare.sqlite")
    try:
        conn.executescript(_old_schema_sql())
        _migrate_add_columns(conn)
        assert conn.execute("SELECT COUNT(*) FROM lessons").fetchone()[0] == 0
        cols = {row["name"] for row in conn.execute("PRAGMA table_info(tasks)")}
        assert "theory" in cols
    finally:
        conn.close()


# === Sync: lessons ===


def test_sync_adds_lessons(temp_db, repo: Path):
    conn = _connect(temp_db)
    try:
        result = sync_from_path(conn, repo)
        conn.commit()
        assert result.lessons_added == 1
        assert result.lessons_updated == 0
        assert result.lessons_deleted == 0
        assert result.errors == 0
        row = conn.execute("SELECT * FROM lessons WHERE id = 'roles'").fetchone()
        assert row["project_id"] == "junior-core"
        assert row["folder_id"] == "block_f_simple"
        assert row["title"] == "Урок roles"
        assert row["order"] == 1
        assert row["version"] == "1.0.0"
        assert len(row["content_hash"]) == 64
        assert "Text." in row["body_md"]
    finally:
        conn.close()


def test_sync_updates_lesson_when_body_changes(temp_db, repo: Path):
    conn = _connect(temp_db)
    try:
        sync_from_path(conn, repo)
        conn.commit()
        before = conn.execute("SELECT content_hash FROM lessons WHERE id = 'roles'").fetchone()[0]

        _write_lesson(_folder_of(repo), "roles", lesson_id="roles", order=1, body="New text.")
        result = sync_from_path(conn, repo)
        conn.commit()
        assert result.lessons_added == 0
        assert result.lessons_updated == 1
        assert result.errors == 0
        row = conn.execute("SELECT content_hash, body_md FROM lessons WHERE id = 'roles'").fetchone()
        assert row["content_hash"] != before
        assert "New text." in row["body_md"]

        # Unchanged content → no lesson churn.
        again = sync_from_path(conn, repo)
        conn.commit()
        assert (again.lessons_added, again.lessons_updated, again.lessons_deleted) == (0, 0, 0)
    finally:
        conn.close()


def test_sync_deletes_lessons_whose_files_disappeared(temp_db, repo: Path):
    conn = _connect(temp_db)
    try:
        _write_lesson(_folder_of(repo), "loops", lesson_id="loops", order=2)
        first = sync_from_path(conn, repo)
        conn.commit()
        assert first.lessons_added == 2
        assert _lesson_ids(conn) == ["loops", "roles"]

        (_folder_of(repo) / "lesson_loops.md").unlink()
        result = sync_from_path(conn, repo)
        conn.commit()
        assert result.lessons_deleted == 1
        assert result.errors == 0
        assert _lesson_ids(conn) == ["roles"]
    finally:
        conn.close()


def test_duplicate_lesson_id_is_sync_error(temp_db, repo: Path):
    conn = _connect(temp_db)
    try:
        _write_lesson(_folder_of(repo), "roles_copy", lesson_id="roles", order=9, body="Dup.")
        result = sync_from_path(conn, repo)
        conn.commit()
        assert result.errors == 1
        assert "duplicate lesson id" in result.error_details_text
        assert "lesson_roles_copy.md" in result.error_details_text
        # Only the first card wins; lesson counts stay clean.
        assert result.lessons_added == 1
        assert _lesson_ids(conn) == ["roles"]
        assert "Text." in conn.execute("SELECT body_md FROM lessons").fetchone()[0]
        # Task F1 itself is unaffected by the duplicate.
        assert conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 1
    finally:
        conn.close()


def test_unparseable_lesson_is_sync_error(temp_db, repo: Path):
    conn = _connect(temp_db)
    try:
        (_folder_of(repo) / "lesson_broken.md").write_text("# no fm\n", encoding="utf-8")
        result = sync_from_path(conn, repo)
        conn.commit()
        assert result.errors == 1
        assert "LESSON lesson_broken.md" in result.error_details_text
    finally:
        conn.close()


# === Sync: task theory ===


def test_theory_refresh_without_version_bump(temp_db, repo: Path):
    conn = _connect(temp_db)
    try:
        first = sync_from_path(conn, repo)
        conn.commit()
        assert first.added == 1
        assert conn.execute(
            "SELECT theory FROM tasks WHERE id = 'F1'"
        ).fetchone()[0] == '["roles"]'

        # Add a second lesson and re-point theory; content and version untouched.
        _write_lesson(_folder_of(repo), "cycles", lesson_id="cycles", order=2)
        _write_task(_folder_of(repo), version="1.0.0", theory=["cycles", "roles"])
        result = sync_from_path(conn, repo)
        conn.commit()
        assert result.errors == 0
        assert "VERSION F1" not in result.error_details_text
        row = conn.execute("SELECT version, theory FROM tasks WHERE id = 'F1'").fetchone()
        assert row["version"] == "1.0.0"
        assert row["theory"] == '["cycles", "roles"]'
        # Theory-only change does not add a task_versions row.
        versions = conn.execute(
            "SELECT COUNT(*) FROM task_versions WHERE task_id = 'F1'"
        ).fetchone()[0]
        assert versions == 1

        # Dropping theory entirely is also refreshed without a bump.
        _write_task(_folder_of(repo), version="1.0.0")
        result = sync_from_path(conn, repo)
        conn.commit()
        assert result.errors == 0
        assert conn.execute(
            "SELECT theory FROM tasks WHERE id = 'F1'"
        ).fetchone()[0] == "[]"
    finally:
        conn.close()


def test_unknown_theory_id_is_warning_not_error(temp_db, repo: Path):
    conn = _connect(temp_db)
    try:
        _write_task(_folder_of(repo), theory=["roles", "missing-lesson"])
        result = sync_from_path(conn, repo)
        conn.commit()
        assert result.errors == 0
        assert result.status == "success"
        assert result.added == 1
        assert "THEORY F1: lesson 'missing-lesson' not found" in result.error_details_text
        # Warning is persisted in sync_log.error_details too.
        details = conn.execute(
            "SELECT error_details, errors FROM sync_log ORDER BY id DESC LIMIT 1"
        ).fetchone()
        assert "missing-lesson" in details["error_details"]
        assert details["errors"] == 0
        # Raw id kept verbatim (clients may resolve it later).
        assert conn.execute(
            "SELECT theory FROM tasks WHERE id = 'F1'"
        ).fetchone()[0] == '["roles", "missing-lesson"]'
    finally:
        conn.close()


def test_invalid_theory_id_warns_without_error(temp_db, repo: Path):
    conn = _connect(temp_db)
    try:
        _write_task(_folder_of(repo), theory=["roles/../x"])
        result = sync_from_path(conn, repo)
        conn.commit()
        assert result.errors == 0
        assert result.added == 1
        assert "invalid lesson id" in result.error_details_text
    finally:
        conn.close()


def test_theory_from_content_change_is_applied_with_version_bump(temp_db, repo: Path):
    conn = _connect(temp_db)
    try:
        sync_from_path(conn, repo)
        conn.commit()
        _write_lesson(_folder_of(repo), "cycles", lesson_id="cycles", order=2)
        _write_task(_folder_of(repo), version="1.1.0", theory=["cycles"], template=_TASK_MD_V2)
        result = sync_from_path(conn, repo)
        conn.commit()
        assert result.updated == 1
        assert result.errors == 0
        row = conn.execute("SELECT version, theory FROM tasks WHERE id = 'F1'").fetchone()
        assert (row["version"], row["theory"]) == ("1.1.0", '["cycles"]')
    finally:
        conn.close()
