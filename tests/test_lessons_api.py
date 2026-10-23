"""Tests for GET /lessons + theory fields on GET /tasks (theory cards API).

Uses the same isolated-DB + dependency-override style as
``tests/test_catalog_archive.py``: catalog rows are seeded directly, then
the ``lessons`` / ``tasks`` routers are mounted on a bare FastAPI app.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ego_server.catalog_visibility import activate_only_projects
from ego_server.db import init_schema
from ego_server.deps import get_current_user, get_db
from ego_server.routers import lessons, tasks


_TS = "2026-10-12T08:00:00+00:00"
_TASK_MD = (
    "# Задача {id}: {title}\n\n"
    "## Условие\nDo the thing.\n\n"
    "<details><summary>Эталонное решение</summary>\n\n"
    "```python\ndef {fn}(value):\n    return value + 1\n```\n\n</details>\n"
)


def _connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _seed(conn: sqlite3.Connection, root: Path) -> None:
    """Two projects (one archived), two folders, 2 lessons, 2 tasks."""
    for project_id, name, order in [("old", "Old track", 5), ("core", "Core track", 1)]:
        conn.execute(
            'INSERT INTO projects (id, name, "order", created_at, updated_at) '
            "VALUES (?, ?, ?, ?, ?)",
            (project_id, name, order, _TS, _TS),
        )
    for folder_id, project_id, code, name, order in [
        ("intro", "old", "I", "Введение", 1),
        ("basics", "core", "B", "Основы", 2),
    ]:
        conn.execute(
            'INSERT INTO folders (id, project_id, code, name, "order", created_at, updated_at) '
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (folder_id, project_id, code, name, order, _TS, _TS),
        )
    for lesson_id, project_id, folder_id, title, order in [
        ("roles-counter", "core", "basics", "Счётчик", 2),
        ("roles-accumulator", "core", "basics", "Накопитель", 1),
        ("old-lesson", "old", "intro", "Старое", 0),
    ]:
        conn.execute(
            'INSERT INTO lessons (id, project_id, folder_id, title, "order", version, '
            "content_hash, body_md, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, '1.0.0', ?, ?, ?, ?)",
            (
                lesson_id,
                project_id,
                folder_id,
                title,
                order,
                f"hash-{lesson_id}",
                f"# {title}\n\nОтсортированный текст.",
                _TS,
                _TS,
            ),
        )
    for task_id, project_id, folder_id, block, title, theory in [
        ("B1", "core", "basics", "B", "Core task", '["roles-accumulator", "roles-counter"]'),
        ("I1", "old", "intro", "I", "Old task", "[]"),
        ("ORPHAN", None, None, "B", "Legacy task", "[]"),
    ]:
        folder_dir = root / (project_id or "unassigned")
        folder_dir.mkdir(parents=True, exist_ok=True)
        md_path = folder_dir / f"task_{task_id.lower()}.md"
        md_path.write_text(
            _TASK_MD.format(id=task_id, title=title, fn=f"task_{task_id.lower()}"),
            encoding="utf-8",
        )
        conn.execute(
            "INSERT INTO tasks (id, block, slug, task_id, title, level, version, content_hash, "
            "md_path, folder_id, project_id, theory, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, 'easy', '1.0.0', ?, ?, ?, ?, ?, ?, ?)",
            (
                task_id,
                block,
                folder_id or "unassigned",
                task_id,
                title,
                f"hash-{task_id}",
                str(md_path),
                folder_id,
                project_id,
                theory,
                _TS,
                _TS,
            ),
        )
    conn.commit()


@pytest.fixture
def api_db(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    conn = _connect(tmp_path / "lessons.sqlite")
    init_schema(conn)
    _seed(conn, tmp_path / "content")
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def api_client(api_db: sqlite3.Connection, tmp_path: Path) -> Iterator[TestClient]:
    app = FastAPI()
    app.include_router(tasks.router, prefix="/tasks")
    app.include_router(lessons.router, prefix="/lessons")

    def isolated_db() -> Iterator[sqlite3.Connection]:
        conn = _connect(tmp_path / "lessons.sqlite")
        try:
            yield conn
        finally:
            conn.close()

    app.dependency_overrides[get_db] = isolated_db
    app.dependency_overrides[get_current_user] = lambda: {"sub": "learner", "role": "student"}
    with TestClient(app) as client:
        yield client


def _get_json(client: TestClient, path: str, **kwargs):
    response = client.get(path, **kwargs)
    assert response.status_code == 200, response.text
    return response.json()


# === GET /lessons ===


def test_lessons_require_auth(tmp_path: Path):
    from ego_server.main import app

    with TestClient(app) as client:
        assert client.get("/lessons").status_code == 401
        assert client.get("/lessons/roles-accumulator").status_code == 401


def test_list_lessons_fields_and_order(api_client: TestClient):
    data = _get_json(api_client, "/lessons")
    # project_order (core=1 < old=5) → folder_order → lesson order → id.
    assert [lesson["id"] for lesson in data] == ["roles-accumulator", "roles-counter", "old-lesson"]
    first = data[2]
    assert set(first) == {
        "id",
        "project_id",
        "folder_id",
        "block",
        "title",
        "order",
        "version",
        "content_hash",
    }
    assert first == {
        "id": "old-lesson",
        "project_id": "old",
        "folder_id": "intro",
        "block": "I",  # folder code == TaskMeta.block of that folder
        "title": "Старое",
        "order": 0,
        "version": "1.0.0",
        "content_hash": "hash-old-lesson",
    }
    # body is not part of the list payload.
    assert "body_md" not in first


def test_list_lessons_filter_by_folder(api_client: TestClient):
    data = _get_json(api_client, "/lessons", params={"folder_id": "basics"})
    assert [lesson["id"] for lesson in data] == ["roles-accumulator", "roles-counter"]
    assert _get_json(api_client, "/lessons", params={"folder_id": "nope"}) == []


def test_hidden_project_hides_lessons(api_db: sqlite3.Connection, api_client: TestClient):
    activate_only_projects(api_db, ["core"])
    api_db.commit()

    data = _get_json(api_client, "/lessons")
    assert {lesson["id"] for lesson in data} == {"roles-accumulator", "roles-counter"}
    response = api_client.get("/lessons/old-lesson")
    assert response.status_code == 404


# === GET /lessons/<id> ===


def test_get_lesson_with_body(api_client: TestClient):
    data = _get_json(api_client, "/lessons/roles-accumulator")
    assert data["id"] == "roles-accumulator"
    assert data["block"] == "B"
    assert data["title"] == "Накопитель"
    assert data["order"] == 1
    assert "Отсортированный текст." in data["body_md"]


@pytest.mark.parametrize("lesson_id", ["missing", "roles%2F..%2Fx", "-bad"])
def test_get_lesson_unknown_is_404(api_client: TestClient, lesson_id: str):
    response = api_client.get(f"/lessons/{lesson_id}")
    assert response.status_code in (404, 422), response.text


# === GET /tasks theory + catalog fields ===


def test_task_list_has_theory_and_catalog_fields(api_client: TestClient):
    data = {task["id"]: task for task in _get_json(api_client, "/tasks")}
    core = data["B1"]
    assert core["project_id"] == "core"
    assert core["project_name"] == "Core track"
    assert core["project_order"] == 1
    assert core["folder_id"] == "basics"
    assert core["folder_name"] == "Основы"
    assert core["folder_order"] == 2
    assert core["theory"] == ["roles-accumulator", "roles-counter"]

    orphan = data["ORPHAN"]
    assert orphan["project_id"] is None
    assert orphan["project_name"] is None
    assert orphan["project_order"] == 0
    assert orphan["folder_id"] is None
    assert orphan["folder_name"] is None
    assert orphan["folder_order"] == 0
    assert orphan["theory"] == []


def test_get_task_full_has_theory_and_catalog_fields(api_client: TestClient):
    data = _get_json(api_client, "/tasks/B1")
    assert data["theory"] == ["roles-accumulator", "roles-counter"]
    assert data["project_name"] == "Core track"
    assert data["folder_name"] == "Основы"
    assert data["project_order"] == 1
    assert data["folder_order"] == 2


def test_get_task_legacy_fields_default(api_client: TestClient):
    data = _get_json(api_client, "/tasks/ORPHAN")
    assert data["project_id"] is None
    assert data["folder_id"] is None
    assert data["theory"] == []
