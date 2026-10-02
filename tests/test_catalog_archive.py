"""Reversible catalog selection keeps canonical content and learner history."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ego_server.catalog_visibility import activate_only_projects
from ego_server.db import SCHEMA_PATH, init_schema
from ego_server.deps import get_current_user, get_db
from ego_server.routers import admin, tasks


_HISTORY_TABLES = ("progress", "runs", "task_versions")
_CATALOG_TABLES = ("projects", "folders", "tasks")
_TIMESTAMP = "2026-10-02T08:00:00+00:00"


def _connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _snapshot(conn: sqlite3.Connection, *tables: str) -> dict[str, list[dict]]:
    return {
        table: [
            dict(row)
            for row in conn.execute(f"SELECT rowid AS stored_rowid, * FROM {table} ORDER BY rowid")
        ]
        for table in tables
    }


def _catalog_content(conn: sqlite3.Connection) -> dict[str, list[dict]]:
    return {
        table: [{key: value for key, value in row.items() if key != "archived"} for row in rows]
        for table, rows in _snapshot(conn, *_CATALOG_TABLES).items()
    }


def _flags(conn: sqlite3.Connection, table: str) -> dict[str, int]:
    return dict(conn.execute(f"SELECT id, archived FROM {table} ORDER BY id"))


def _seed_catalog(conn: sqlite3.Connection, content_root: Path) -> dict[str, Path]:
    for order, (project_id, name) in enumerate(
        [("legacy", "Legacy course"), ("xl-a", "XL-A"), ("zz-empty", "Empty import")]
    ):
        conn.execute(
            'INSERT INTO projects (id, name, "order", created_at, updated_at) VALUES (?, ?, ?, ?, ?)',
            (project_id, name, order, _TIMESTAMP, _TIMESTAMP),
        )
    for project_id, code in [("legacy", "OLD"), ("xl-a", "XL-A")]:
        conn.execute(
            "INSERT INTO folders (id, project_id, code, name, level, created_at, updated_at) "
            "VALUES ('practice', ?, ?, ?, 'easy', ?, ?)",
            (project_id, code, f"{project_id} practice", _TIMESTAMP, _TIMESTAMP),
        )

    paths = {}
    for task_id, project_id, block, title in [
        ("OLD1", "legacy", "OLD", "Historical task"),
        ("OLD2", "legacy", "OLD", "Other old task"),
        ("XL-A01", "xl-a", "XL-A", "Current task one"),
        ("XL-A02", "xl-a", "XL-A", "Current task two"),
        ("ORPHAN", None, "OLD", "Legacy task without a project"),
    ]:
        folder = content_root / (project_id or "unassigned") / "practice"
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"task_{task_id.lower()}.md"
        path.write_text(
            f"# Задача {task_id}: {title}\n\n"
            f"**Блок:** {block}\n\n"
            "## Условие\nReturn the value plus one.\n\n"
            "## Правила\nKeep the original input unchanged.\n",
            encoding="utf-8",
        )
        function_name = f"task_{task_id.lower().replace('-', '_')}"
        path.with_suffix(".solution.py").write_text(
            f"def {function_name}(value):\n    return value + 1\n",
            encoding="utf-8",
        )
        paths[task_id] = path
        conn.execute(
            "INSERT INTO tasks (id, block, slug, task_id, title, level, version, "
            "content_hash, md_path, folder_id, project_id, created_at, updated_at) "
            "VALUES (?, ?, 'practice', ?, ?, 'easy', '2.3.0', ?, ?, ?, ?, ?, ?)",
            (
                task_id,
                block,
                task_id,
                title,
                f"hash-{task_id}",
                str(path),
                "practice" if project_id else None,
                project_id,
                _TIMESTAMP,
                _TIMESTAMP,
            ),
        )
        conn.execute(
            "INSERT INTO task_versions (task_id, version, content_hash, breaking, md_path, created_at) "
            "VALUES (?, '2.3.0', ?, 0, ?, ?)",
            (task_id, f"hash-{task_id}", str(path), _TIMESTAMP),
        )
    conn.execute(
        "INSERT INTO task_versions (task_id, version, content_hash, breaking, md_path, created_at) "
        "VALUES ('OLD1', '1.0.0', 'previous-hash', 1, ?, '2026-09-01T09:00:00+00:00')",
        (str(paths["OLD1"]),),
    )
    conn.executemany(
        "INSERT INTO students (id, username, role, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
        [
            ("learner", "learner", "student", "unused", _TIMESTAMP),
            ("operator", "operator", "admin", "unused", _TIMESTAMP),
        ],
    )
    conn.executemany(
        "INSERT INTO progress (student_id, task_id, version, status, attempts, passed_tests, "
        "total_tests, last_run_at) VALUES ('learner', ?, ?, ?, ?, ?, ?, ?)",
        [
            ("OLD1", "1.0.0", "passed", 3, 8, 8, "2026-09-01T09:30:00+00:00"),
            ("OLD1", "2.3.0", "partial", 2, 5, 8, _TIMESTAMP),
            ("XL-A01", "2.3.0", "passed", 1, 3, 3, _TIMESTAMP),
        ],
    )
    conn.executemany(
        "INSERT INTO runs (id, student_id, task_id, version, solution_hash, status, log, created_at) "
        "VALUES (?, 'learner', ?, ?, ?, ?, ?, ?)",
        [
            (
                "old-pass",
                "OLD1",
                "1.0.0",
                "solution-before",
                "passed",
                '{"stdout":"старый результат\\n", "tests":8}',
                "2026-09-01T09:30:00+00:00",
            ),
            ("old-fail", "OLD1", "2.3.0", "solution-after", "failed", "5/8\nkeep log", _TIMESTAMP),
            ("new-pass", "XL-A01", "2.3.0", "new-solution", "passed", "3/3", _TIMESTAMP),
        ],
    )
    conn.commit()
    return paths


@pytest.fixture
def archive_db(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    conn = _connect(tmp_path / "archive.sqlite")
    init_schema(conn)
    _seed_catalog(conn, tmp_path / "content")
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def archive_client(archive_db: sqlite3.Connection, tmp_path: Path) -> Iterator[TestClient]:
    app = FastAPI()
    app.include_router(tasks.router, prefix="/tasks")
    app.include_router(admin.router, prefix="/admin")

    def isolated_db() -> Iterator[sqlite3.Connection]:
        conn = _connect(tmp_path / "archive.sqlite")
        try:
            yield conn
        finally:
            conn.close()

    app.dependency_overrides[get_db] = isolated_db
    app.dependency_overrides[get_current_user] = lambda: {"sub": "operator", "role": "admin"}
    with TestClient(app) as client:
        yield client


def _get_json(client: TestClient, path: str, **kwargs):
    response = client.get(path, **kwargs)
    assert response.status_code == 200, response.text
    return response.json()


def _catalog_task_ids(catalog: dict) -> set[str]:
    return {
        task["id"]
        for project in catalog["projects"]
        for folder in project["folders"]
        for task in folder["tasks"]
    }


def test_activate_only_projects_filters_task_lists_and_catalog(archive_db, archive_client):
    result = activate_only_projects(archive_db, ["xl-a"])
    archive_db.commit()

    assert result == {"active_projects": ["xl-a"], "active_tasks": 2, "archived_tasks": 3}
    assert {task["id"] for task in _get_json(archive_client, "/tasks")} == {"XL-A01", "XL-A02"}
    assert _get_json(archive_client, "/tasks", params={"block": "OLD"}) == []
    assert {
        task["id"] for task in _get_json(archive_client, "/tasks", params={"block": "XL-A"})
    } == {"XL-A01", "XL-A02"}
    catalog = _get_json(archive_client, "/admin/catalog")
    assert [project["id"] for project in catalog["projects"]] == ["xl-a"]
    assert [folder["id"] for folder in catalog["projects"][0]["folders"]] == ["practice"]
    assert _catalog_task_ids(catalog) == {"XL-A01", "XL-A02"}
    for query in ("legacy", "Historical task", "ORPHAN"):
        assert _get_json(archive_client, "/admin/catalog", params={"q": query}) == {"projects": []}


def test_overview_counts_only_visible_catalog_and_keeps_students(archive_db, archive_client):
    activate_only_projects(archive_db, ["xl-a"])
    archive_db.commit()

    overview = _get_json(archive_client, "/admin/overview")
    assert overview["server"] == "ok"
    assert overview["counts"] == {"projects": 1, "folders": 1, "tasks": 2, "students": 1}
    assert overview["latest_sync"] is None


def test_archive_preserves_all_history_rows_catalog_content_and_source_files(archive_db, tmp_path):
    history_before = _snapshot(archive_db, *_HISTORY_TABLES)
    catalog_before = _catalog_content(archive_db)
    files_before = {
        path: path.read_bytes() for path in (tmp_path / "content").rglob("*") if path.is_file()
    }

    activate_only_projects(archive_db, ["xl-a"])
    archive_db.commit()

    assert _snapshot(archive_db, *_HISTORY_TABLES) == history_before
    assert _catalog_content(archive_db) == catalog_before
    assert {path: path.read_bytes() for path in files_before} == files_before
    assert _flags(archive_db, "projects") == {"legacy": 1, "xl-a": 0, "zz-empty": 1}
    assert _flags(archive_db, "tasks") == {
        "OLD1": 1,
        "OLD2": 1,
        "ORPHAN": 1,
        "XL-A01": 0,
        "XL-A02": 0,
    }


@pytest.mark.parametrize("role", ["student", "admin"])
def test_archived_historical_task_remains_readable_with_role_based_solution(
    archive_db, archive_client, role
):
    activate_only_projects(archive_db, ["xl-a"])
    archive_db.commit()
    archive_client.app.dependency_overrides[get_current_user] = lambda: {
        "sub": "learner" if role == "student" else "operator",
        "role": role,
    }
    md_path = Path(archive_db.execute("SELECT md_path FROM tasks WHERE id = 'OLD1'").fetchone()[0])

    body = _get_json(archive_client, "/tasks/OLD1", params={"include_solution": "true"})

    assert body["id"] == "OLD1"
    assert body["title"] == "Historical task"
    assert body["version"] == "2.3.0"
    assert "Return the value plus one." in body["statement_md"]
    assert "def task_old1(value):" in body["stub_py"]
    expected_solution = md_path.with_suffix(".solution.py").read_text(encoding="utf-8")
    assert body["solution_py"] == (expected_solution if role == "admin" else "")


@pytest.mark.parametrize(
    "selection",
    [[], ["missing"], ["zz-empty"], ["xl-a", "zzz-missing"], ["xl-a", "zz-empty"]],
    ids=["empty", "unknown", "unpopulated", "valid-then-unknown", "valid-then-unpopulated"],
)
def test_invalid_selection_is_rejected_before_any_write(archive_db, selection):
    activate_only_projects(archive_db, ["legacy"])
    archive_db.commit()
    before = _snapshot(archive_db, *_CATALOG_TABLES, *_HISTORY_TABLES)
    changes_before = archive_db.total_changes
    assert not archive_db.in_transaction

    with pytest.raises(ValueError):
        activate_only_projects(archive_db, selection)

    assert archive_db.total_changes == changes_before
    assert not archive_db.in_transaction
    assert _snapshot(archive_db, *_CATALOG_TABLES, *_HISTORY_TABLES) == before


def test_selection_is_idempotent_and_old_project_can_be_restored(archive_db, archive_client):
    history_before = _snapshot(archive_db, *_HISTORY_TABLES)
    first = activate_only_projects(archive_db, ["xl-a", "xl-a"])
    archive_db.commit()
    selected = _snapshot(archive_db, *_CATALOG_TABLES, *_HISTORY_TABLES)

    assert activate_only_projects(archive_db, ["xl-a"]) == first
    archive_db.commit()
    assert _snapshot(archive_db, *_CATALOG_TABLES, *_HISTORY_TABLES) == selected
    assert activate_only_projects(archive_db, ["legacy"]) == {
        "active_projects": ["legacy"],
        "active_tasks": 2,
        "archived_tasks": 3,
    }
    archive_db.commit()

    assert {task["id"] for task in _get_json(archive_client, "/tasks")} == {"OLD1", "OLD2"}
    catalog = _get_json(archive_client, "/admin/catalog")
    assert [project["id"] for project in catalog["projects"]] == ["legacy"]
    assert _catalog_task_ids(catalog) == {"OLD1", "OLD2"}
    assert _flags(archive_db, "projects") == {"legacy": 0, "xl-a": 1, "zz-empty": 1}
    assert _snapshot(archive_db, *_HISTORY_TABLES) == history_before


def test_archived_project_alone_hides_tasks_whose_own_flags_are_active(archive_db, archive_client):
    archive_db.execute("UPDATE projects SET archived = 1 WHERE id = 'legacy'")
    archive_db.commit()
    assert (
        archive_db.execute(
            "SELECT COUNT(*) FROM tasks WHERE project_id = 'legacy' AND archived = 0"
        ).fetchone()[0]
        == 2
    )

    assert {task["id"] for task in _get_json(archive_client, "/tasks")} == {
        "XL-A01",
        "XL-A02",
        "ORPHAN",
    }
    assert {
        task["id"] for task in _get_json(archive_client, "/tasks", params={"block": "OLD"})
    } == {"ORPHAN"}
    catalog = _get_json(archive_client, "/admin/catalog")
    assert {project["id"] for project in catalog["projects"]} == {"xl-a", "zz-empty"}
    assert _catalog_task_ids(catalog) == {"XL-A01", "XL-A02"}
    assert _get_json(archive_client, "/admin/catalog", params={"q": "legacy"}) == {"projects": []}
    assert _get_json(archive_client, "/admin/overview")["counts"] == {
        "projects": 2,
        "folders": 1,
        "tasks": 3,
        "students": 1,
    }


def test_archived_task_alone_is_hidden_inside_visible_project(archive_db, archive_client):
    activate_only_projects(archive_db, ["xl-a"])
    archive_db.execute("UPDATE tasks SET archived = 1 WHERE id = 'XL-A02'")
    archive_db.commit()

    assert {task["id"] for task in _get_json(archive_client, "/tasks")} == {"XL-A01"}
    assert _catalog_task_ids(_get_json(archive_client, "/admin/catalog")) == {"XL-A01"}
    assert _get_json(archive_client, "/admin/overview")["counts"] == {
        "projects": 1,
        "folders": 1,
        "tasks": 1,
        "students": 1,
    }


def test_visibility_changes_remain_in_callers_transaction(archive_db):
    before = _snapshot(archive_db, *_CATALOG_TABLES, *_HISTORY_TABLES)

    activate_only_projects(archive_db, ["xl-a"])
    assert archive_db.in_transaction
    archive_db.rollback()

    assert _snapshot(archive_db, *_CATALOG_TABLES, *_HISTORY_TABLES) == before


def test_migration_adds_active_defaults_and_reinitialization_keeps_archives(tmp_path):
    conn = _connect(tmp_path / "legacy.sqlite")
    try:
        # Reproduce the immediately preceding schema, which has no archive flags.
        old_schema = "\n".join(
            line
            for line in SCHEMA_PATH.read_text(encoding="utf-8").splitlines()
            if not line.strip().startswith("archived ")
        )
        conn.executescript(old_schema)
        _seed_catalog(conn, tmp_path / "legacy-content")
        for table in ("projects", "tasks"):
            assert "archived" not in {
                row["name"] for row in conn.execute(f"PRAGMA table_info({table})")
            }
        history_before = _snapshot(conn, *_HISTORY_TABLES)
        content_before = _catalog_content(conn)

        init_schema(conn)

        assert _flags(conn, "projects") == {"legacy": 0, "xl-a": 0, "zz-empty": 0}
        assert _flags(conn, "tasks") == {
            "OLD1": 0,
            "OLD2": 0,
            "ORPHAN": 0,
            "XL-A01": 0,
            "XL-A02": 0,
        }
        assert _snapshot(conn, *_HISTORY_TABLES) == history_before
        assert _catalog_content(conn) == content_before
        activate_only_projects(conn, ["xl-a"])
        conn.commit()
        archived = _snapshot(conn, *_CATALOG_TABLES, *_HISTORY_TABLES)

        init_schema(conn)
        init_schema(conn)

        assert _snapshot(conn, *_CATALOG_TABLES, *_HISTORY_TABLES) == archived
    finally:
        conn.close()
