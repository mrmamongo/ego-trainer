"""Soft course recommendations + exam-kind breakdown.

Covers:
- ``recommended_after`` parsing (``project.yaml``) and storage by sync;
- additive migration of ``projects.recommended_after`` on an old DB;
- ``GET /projects`` readiness math (incl. ``min_per_kind``);
- ``GET /progress/me/breakdown`` / ``GET /progress/{student}/breakdown``
  and role checks;
- the recommendation never blocks anything (checks/progress keep working).
"""

from __future__ import annotations

import importlib
import sqlite3
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ego.catalog import parse_project
from ego_server.recommendations import RecommendedAfter, compute_breakdown, compute_readiness


# === Fixtures ===


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

    with TestClient(app) as c:
        yield c


_PROJECT_YAML = """id: {id}
name: "{name}"
version: "1.0.0"
order: {order}
version_policy: declare
{recommended}"""

_RECOMMENDED = """recommended_after:
  project: xl-a
  min_passed: 3
  min_per_kind: 1
  note: "Курс ООП рекомендуем начинать после экзамена XL-A"
"""

_TASK_MD = """---
id: {id}
title: '{id}'
version: '1.0.0'
level: easy
tags: [{tags}]
---

# Задача {id}: проверка тэгов

**Сложность:** easy

## Условие

Do the thing.

<details><summary>Эталонное решение</summary>

```python
def task_{fn}():
    return 42
```

</details>
"""

#: (task id, tags) of XL-A — two of each kind plus one extra tag.
_XL_A_TASKS = [
    ("XL-A01", "bug, chat"),
    ("XL-A02", "bug, chat"),
    ("XL-A03", "modify, chat"),
    ("XL-A04", "modify, chat"),
    ("XL-A05", "new, agents"),
    ("XL-A06", "new, agents"),
]


@pytest.fixture
def catalog_repo(tmp_path: Path) -> Path:
    """Content-repo: prerequisite ``xl-a`` + ``oop`` recommending it."""
    root = tmp_path / "ego-tasks"
    root.mkdir()
    (root / "catalog.yaml").write_text(
        "schema_version: 1\n"
        "projects:\n"
        "  - id: xl-a\n"
        "    path: projects/xl-a\n"
        "    enabled: true\n"
        "  - id: oop\n"
        "    path: projects/oop\n"
        "    enabled: true\n"
        "  - id: plain\n"
        "    path: projects/plain\n"
        "    enabled: true\n",
        encoding="utf-8",
    )
    _write_project(
        root, "xl-a", "XL-A", order=1, recommended=""
    )
    _write_tasks(root, "xl-a", _XL_A_TASKS)
    _write_project(
        root, "oop", "ООП", order=2, recommended=_RECOMMENDED
    )
    _write_tasks(root, "oop", [("OOP1", "classes")])
    _write_project(root, "plain", "Без рекомендаций", order=3, recommended="")
    _write_tasks(root, "plain", [("P1", "basics")])
    return root


def _write_project(root: Path, project_id: str, name: str, *, order: int, recommended: str) -> None:
    proj = root / "projects" / project_id
    (proj / "folders").mkdir(parents=True)
    (proj / "project.yaml").write_text(
        _PROJECT_YAML.format(id=project_id, name=name, order=order, recommended=recommended),
        encoding="utf-8",
    )


def _write_tasks(root: Path, project_id: str, tasks: list[tuple[str, str]]) -> None:
    folder = root / "projects" / project_id / "folders" / f"{project_id}_tasks"
    folder.mkdir()
    (folder / "folder.yaml").write_text(
        f"id: {project_id}_tasks\ncode: T\nname: 'Tasks'\n", encoding="utf-8"
    )
    for task_id, tags in tasks:
        fn = task_id.lower().replace("-", "_")
        (folder / f"task_{fn}.md").write_text(
            _TASK_MD.format(id=task_id, tags=tags, fn=fn), encoding="utf-8"
        )


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def _student(client, name="alice"):
    from tests.conftest import create_test_user

    return create_test_user(client, name, "pw", "student")


def _passed(client, token, task_id, status="passed"):
    r = client.post(
        "/progress/push",
        json={
            "task_id": task_id,
            "version": "1.0.0",
            "solution_hash": "a" * 64,
            "status": status,
            "log": "",
            "passed_tests": 1,
            "total_tests": 1,
        },
        headers=_auth_headers(token),
    )
    assert r.status_code == 200, r.text


def _sync(client, repo: Path) -> dict:
    from tests.conftest import create_test_user

    token, _ = create_test_user(client, "sync-admin", "pw", "admin")
    r = client.post("/admin/sync-tasks", json={"path": str(repo)}, headers=_auth_headers(token))
    assert r.status_code == 200, r.text
    return r.json()


def _project(client, token, project_id) -> dict:
    r = client.get("/projects", headers=_auth_headers(token))
    assert r.status_code == 200, r.text
    return next(p for p in r.json() if p["id"] == project_id)


# === Catalog model ===


def test_project_yaml_parses_recommended_after():
    project = parse_project(
        "id: oop\nname: OOP\nrecommended_after:\n  project: xl-a\n"
        "  min_passed: 21\n  note: 'После экзамена'\n"
    )
    assert project.recommended_after is not None
    assert project.recommended_after.project == "xl-a"
    assert project.recommended_after.min_passed == 21
    assert project.recommended_after.min_per_kind is None
    assert project.recommended_after.note == "После экзамена"


def test_project_yaml_without_recommendation_is_none():
    assert parse_project("id: oop\nname: OOP\n").recommended_after is None


# === Sync ===


def test_sync_stores_recommended_after(temp_db, catalog_repo: Path):
    from ego_server.sync import sync_from_path

    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    try:
        result = sync_from_path(conn, catalog_repo)
        conn.commit()
        assert result.errors == 0
        rows = {
            row["id"]: row["recommended_after"]
            for row in conn.execute("SELECT id, recommended_after FROM projects")
        }
        assert rows["oop"] is not None
        import json

        assert json.loads(rows["oop"]) == {
            "project": "xl-a",
            "min_passed": 3,
            "min_per_kind": 1,
            "note": "Курс ООП рекомендуем начинать после экзамена XL-A",
        }
        assert rows["xl-a"] is None
        assert rows["plain"] is None
    finally:
        conn.close()


def test_sync_updates_and_clears_recommended_after(temp_db, catalog_repo: Path):
    from ego_server.sync import sync_from_path

    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    try:
        sync_from_path(conn, catalog_repo)
        conn.commit()
        py = catalog_repo / "projects" / "oop" / "project.yaml"
        py.write_text(
            _PROJECT_YAML.format(
                id="oop", name="ООП", order=2,
                recommended="recommended_after:\n  project: xl-a\n  min_passed: 5\n",
            ),
            encoding="utf-8",
        )
        sync_from_path(conn, catalog_repo)
        conn.commit()
        assert "5" in conn.execute(
            "SELECT recommended_after FROM projects WHERE id = 'oop'"
        ).fetchone()[0]

        py.write_text(
            _PROJECT_YAML.format(id="oop", name="ООП", order=2, recommended=""),
            encoding="utf-8",
        )
        sync_from_path(conn, catalog_repo)
        conn.commit()
        assert conn.execute(
            "SELECT recommended_after FROM projects WHERE id = 'oop'"
        ).fetchone()[0] is None
    finally:
        conn.close()


# === Migration ===


def test_old_projects_table_migrates(temp_db, tmp_path: Path):
    """A DB created before ``recommended_after`` gets the column (additive)."""
    from ego_server.db import _migrate_add_columns

    old = tmp_path / "old.db"
    conn = sqlite3.connect(old)
    conn.row_factory = sqlite3.Row
    try:
        # Pre-``recommended_after`` tables (no lessons/analytics/oauth either).
        conn.executescript(
            """CREATE TABLE projects (
              id TEXT PRIMARY KEY, name TEXT NOT NULL,
              description TEXT NOT NULL DEFAULT '', version TEXT NOT NULL DEFAULT '1.0.0',
              "order" INTEGER NOT NULL DEFAULT 0, default_locale TEXT NOT NULL DEFAULT 'ru',
              tags TEXT NOT NULL DEFAULT '[]', version_policy TEXT NOT NULL DEFAULT 'declare',
              created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
            CREATE TABLE tasks (
              id TEXT PRIMARY KEY, block TEXT NOT NULL, slug TEXT NOT NULL,
              task_id TEXT NOT NULL, title TEXT NOT NULL, level TEXT NOT NULL,
              tags TEXT NOT NULL DEFAULT '[]', version TEXT NOT NULL,
              content_hash TEXT NOT NULL, breaking INTEGER NOT NULL DEFAULT 0,
              md_path TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
              UNIQUE(block, task_id));
            CREATE TABLE oauth_flows (state_hash TEXT PRIMARY KEY);"""
        )
        conn.execute(
            "INSERT INTO projects (id, name, created_at, updated_at) "
            "VALUES ('xl-a', 'XL-A', '2026-01-01', '2026-01-01')"
        )
        conn.commit()
        cols = {row["name"] for row in conn.execute("PRAGMA table_info(projects)")}
        assert "recommended_after" not in cols

        _migrate_add_columns(conn)
        _migrate_add_columns(conn)  # idempotent

        cols = {row["name"] for row in conn.execute("PRAGMA table_info(projects)")}
        assert "recommended_after" in cols
        row = conn.execute("SELECT recommended_after FROM projects WHERE id = 'xl-a'").fetchone()
        assert row["recommended_after"] is None
    finally:
        conn.close()


# === Readiness math (pure) ===


def _rec(**over):
    base = {"project": "xl-a", "min_passed": 3}
    base.update(over)
    return RecommendedAfter(**base)


_TAGS = [("A1", ["bug"]), ("A2", ["bug"]), ("A3", ["modify"]), ("A4", ["modify"]), ("A5", ["new"])]


def test_readiness_counts_passed_and_met_flag():
    ready = compute_readiness(_rec(), _TAGS, {"A1", "A2", "A3"})
    assert (ready.met, ready.passed, ready.required) == (True, 3, 3)
    assert ready.per_kind == {}
    not_ready = compute_readiness(_rec(), _TAGS, {"A1", "A2"})
    assert (not_ready.met, not_ready.passed) == (False, 2)


def test_readiness_min_per_kind():
    rec = _rec(min_passed=1, min_per_kind=2)
    tags = _TAGS + [("A6", ["new"])]
    # 5 passed, but only one ``new`` → not met.
    ready = compute_readiness(rec, tags, {"A1", "A2", "A3", "A4", "A6"})
    assert ready.met is False
    assert ready.per_kind == {"bug": 2, "modify": 2, "new": 1}
    # All thresholds reached (min_passed and every kind).
    met = compute_readiness(rec, tags, {"A1", "A2", "A3", "A4", "A5", "A6"})
    assert met.met is True


def test_readiness_ignores_unknown_task_ids():
    ready = compute_readiness(_rec(min_passed=1), _TAGS, {"ZZZ"})
    assert (ready.met, ready.passed) == (False, 0)


def test_compute_breakdown_splits_kinds_and_other_tags():
    kinds, tags = compute_breakdown(
        [("A1", ["bug", "chat"]), ("A2", ["chat"]), ("A3", ["new", "agents"])], {"A1", "A2"}
    )
    assert kinds == {
        "bug": {"passed": 1, "total": 1},
        "modify": {"passed": 0, "total": 0},
        "new": {"passed": 0, "total": 1},
    }
    assert tags == {"chat": {"passed": 2, "total": 2}, "agents": {"passed": 0, "total": 1}}


# === GET /projects ===


def test_projects_requires_auth(client):
    assert client.get("/projects").status_code == 401


def test_projects_readiness_for_current_user(client, catalog_repo: Path):
    _sync(client, catalog_repo)
    token, _ = _student(client)
    projects = client.get("/projects", headers=_auth_headers(token)).json()
    assert [p["id"] for p in projects] == ["xl-a", "oop", "plain"]
    by_id = {p["id"]: p for p in projects}
    assert by_id["xl-a"]["recommended_after"] is None
    assert by_id["xl-a"]["readiness"] is None
    assert by_id["oop"]["recommended_after"] == {
        "project": "xl-a",
        "min_passed": 3,
        "min_per_kind": 1,
        "note": "Курс ООП рекомендуем начинать после экзамена XL-A",
    }
    assert by_id["oop"]["readiness"] == {
        "met": False,
        "passed": 0,
        "required": 3,
        "per_kind": {"bug": 0, "modify": 0, "new": 0},
    }
    assert by_id["oop"]["order"] == 2
    assert by_id["oop"]["name"] == "ООП"


def test_projects_readiness_met_after_passing_prerequisite(client, catalog_repo: Path):
    _sync(client, catalog_repo)
    token, _ = _student(client)
    # The fixture asks for min_passed=3 AND min_per_kind=1 (bug/modify/new).
    for task_id in ("XL-A01", "XL-A02", "XL-A03"):
        _passed(client, token, task_id)
    assert _project(client, token, "oop")["readiness"]["met"] is False
    _passed(client, token, "XL-A05")
    readiness = _project(client, token, "oop")["readiness"]
    assert readiness == {
        "met": True,
        "passed": 4,
        "required": 3,
        "per_kind": {"bug": 2, "modify": 1, "new": 1},
    }


def test_projects_min_per_kind_blocks_readiness_only_softly(client, catalog_repo: Path):
    _sync(client, catalog_repo)
    token, _ = _student(client)
    # 3 passed (min_passed met) but no passed ``new`` task — recommendation unmet.
    for task_id in ("XL-A01", "XL-A02", "XL-A03"):
        _passed(client, token, task_id)
    readiness = _project(client, token, "oop")["readiness"]
    assert readiness["per_kind"]["new"] == 0

    # The unmet recommendation never blocks work in ``oop``.
    _passed(client, token, "OOP1")
    assert client.get("/tasks/OOP1", headers=_auth_headers(token)).status_code == 200

    # Several passed rows for one task still count once.
    _passed(client, token, "XL-A01")
    got = _project(client, token, "oop")["readiness"]
    assert got["passed"] == 3


def test_projects_stale_progress_does_not_count(temp_db, client, catalog_repo: Path):
    _sync(client, catalog_repo)
    token, student_id = _student(client)
    _passed(client, token, "XL-A01")
    from ego_server.db import get_connection

    conn = get_connection()
    try:
        conn.execute(
            "UPDATE progress SET status = 'stale' WHERE student_id = ? AND task_id = 'XL-A01'",
            (student_id,),
        )
        conn.commit()
    finally:
        conn.close()
    assert _project(client, token, "oop")["readiness"]["passed"] == 0


# === GET /progress/me/breakdown ===


def test_breakdown_requires_auth(client):
    assert client.get("/progress/me/breakdown?project=xl-a").status_code == 401


def test_breakdown_for_me(client, catalog_repo: Path):
    _sync(client, catalog_repo)
    token, _ = _student(client)
    _passed(client, token, "XL-A01")
    _passed(client, token, "XL-A03", status="partial")
    r = client.get("/progress/me/breakdown?project=xl-a", headers=_auth_headers(token))
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["project"] == "xl-a"
    assert data["kinds"] == {
        "bug": {"passed": 1, "total": 2},
        "modify": {"passed": 0, "total": 2},
        "new": {"passed": 0, "total": 2},
    }
    assert data["tags"] == {"chat": {"passed": 1, "total": 4}, "agents": {"passed": 0, "total": 2}}


def test_breakdown_unknown_project_is_empty(client, catalog_repo: Path):
    _sync(client, catalog_repo)
    token, _ = _student(client)
    data = client.get(
        "/progress/me/breakdown?project=missing", headers=_auth_headers(token)
    ).json()
    assert data["kinds"] == {
        "bug": {"passed": 0, "total": 0},
        "modify": {"passed": 0, "total": 0},
        "new": {"passed": 0, "total": 0},
    }
    assert data["tags"] == {}


# === GET /progress/{student}/breakdown (role checks) ===


def test_student_breakdown_for_other_student_forbidden(client, catalog_repo: Path):
    _sync(client, catalog_repo)
    token, _ = _student(client, "alice")
    _, other_id = _student(client, "bob")
    r = client.get(f"/progress/{other_id}/breakdown?project=xl-a", headers=_auth_headers(token))
    assert r.status_code == 403


def test_student_breakdown_for_self_forbidden(client, catalog_repo: Path):
    _sync(client, catalog_repo)
    token, own_id = _student(client, "alice")
    r = client.get(f"/progress/{own_id}/breakdown?project=xl-a", headers=_auth_headers(token))
    assert r.status_code == 403


@pytest.mark.parametrize("role", ["mentor", "admin"])
def test_mentor_reads_student_breakdown(client, catalog_repo: Path, role):
    _sync(client, catalog_repo)
    token, student_id = _student(client, "alice")
    for task_id in ("XL-A01", "XL-A05"):
        _passed(client, token, task_id)
    from tests.conftest import create_test_user

    staff_token, _ = create_test_user(client, f"{role}1", "pw", role)
    r = client.get(
        f"/progress/{student_id}/breakdown?project=xl-a", headers=_auth_headers(staff_token)
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["kinds"]["bug"] == {"passed": 1, "total": 2}
    assert data["kinds"]["modify"] == {"passed": 0, "total": 2}
    assert data["kinds"]["new"] == {"passed": 1, "total": 2}
