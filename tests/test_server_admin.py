"""Tests for ego_server admin endpoints and static admin panel serving.

Covers mentor/admin authorization and student summary behavior.
"""

from __future__ import annotations

import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    """Create an isolated temp SQLite DB and point the server config at it."""
    p = tmp_path / "test.db"
    monkeypatch.setenv("EGO_DB_PATH", str(p))

    import ego_server.config
    import ego_server.db

    importlib.reload(ego_server.config)
    importlib.reload(ego_server.db)

    from ego_server.db import init_db

    init_db()
    return p


@pytest.fixture
def client(db_path):
    """FastAPI TestClient backed by the temp DB (lifespan inits schema)."""
    import ego_server.main

    importlib.reload(ego_server.main)
    from ego_server.main import app

    with TestClient(app) as c:
        yield c


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _create_user(client: TestClient, username: str, password: str, role: str) -> tuple[str, str]:
    from ego_server.auth import generate_user_id, hash_password
    from ego_server.db import get_connection

    conn = get_connection()
    try:
        user_id = generate_user_id()
        pwd_hash = hash_password(password)
        conn.execute(
            "INSERT INTO students (id, username, role, password_hash, created_at) "
            "VALUES (?, ?, ?, ?, datetime('now'))",
            (user_id, username, role, pwd_hash),
        )
        conn.commit()
    finally:
        conn.close()

    r = client.post("/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200, f"login failed for {role}: {r.text}"
    return r.json()["access_token"], user_id


def _make_student(
    client: TestClient, username: str = "alice", password: str = "pw"
) -> tuple[str, str]:
    return _create_user(client, username, password, "student")


def test_admin_panel_served(client: TestClient) -> None:
    r = client.get("/admin/")
    assert r.status_code == 200
    assert '<div id="app"' in r.text
    assert "/static/admin/bundle.js" in r.text


def test_static_bundle_served(client: TestClient) -> None:
    r = client.get("/static/admin/bundle.js")
    if r.status_code == 404:
        pytest.skip("admin bundle not built")
    assert r.status_code == 200
    assert "javascript" in (r.headers.get("content-type") or "").lower()


def test_list_students_unauthorized(client: TestClient) -> None:
    assert client.get("/admin/students").status_code == 401


def test_list_students_forbidden_for_student(client: TestClient) -> None:
    token, _ = _make_student(client)
    r = client.get("/admin/students", headers=_auth_headers(token))
    assert r.status_code == 403


def test_list_students_mentor_and_admin(client: TestClient) -> None:
    token, sid = _make_student(client, "student1")
    from ego_server.db import get_connection

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO progress "
            "(student_id, task_id, version, status, attempts, "
            "passed_tests, total_tests, last_run_at) "
            "VALUES (?, 'F1', '1.0.0', 'passed', 1, 3, 3, datetime('now'))",
            (sid,),
        )
        conn.commit()
    finally:
        conn.close()

    m_token, _ = _create_user(client, "mentor1", "pw", "mentor")
    r = client.get("/admin/students", headers=_auth_headers(m_token))
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["username"] == "student1"
    assert data[0]["role"] == "student"
    assert data[0]["tasks_total"] == 1
    assert data[0]["tasks_passed"] == 1
    assert not any(x["username"] in ("mentor1", "admin1") for x in data)

    a_token, _ = _create_user(client, "admin1", "pw", "admin")
    r = client.get("/admin/students", headers=_auth_headers(a_token))
    assert r.status_code == 200
    data = r.json()
    assert any(x["username"] == "student1" for x in data)
    assert all(x["role"] == "student" for x in data)
    assert not any(x["username"] in ("mentor1", "admin1") for x in data)


def test_create_user_admin_only(client: TestClient) -> None:
    a_token, _ = _create_user(client, "admin1", "pw", "admin")
    m_token, _ = _create_user(client, "mentor1", "pw", "mentor")
    s_token, _ = _make_student(client)
    body = {"username": "newu", "password": "pw", "role": "student"}

    r = client.post("/admin/users", json=body, headers=_auth_headers(a_token))
    assert r.status_code == 201
    assert r.json()["username"] == "newu"

    assert client.post("/admin/users", json=body, headers=_auth_headers(m_token)).status_code == 403
    assert client.post("/admin/users", json=body, headers=_auth_headers(s_token)).status_code == 403


def test_create_user_duplicate_409(client: TestClient) -> None:
    a_token, _ = _create_user(client, "admin1", "pw", "admin")
    body = {"username": "dup", "password": "pw", "role": "student"}
    assert client.post("/admin/users", json=body, headers=_auth_headers(a_token)).status_code == 201
    r = client.post("/admin/users", json=body, headers=_auth_headers(a_token))
    assert r.status_code == 409


def test_update_role_admin_only(client: TestClient) -> None:
    a_token, _ = _create_user(client, "admin1", "pw", "admin")
    m_token, _ = _create_user(client, "mentor1", "pw", "mentor")
    s_token, sid = _make_student(client, "student1")
    r = client.put(
        f"/admin/users/{sid}/role",
        json={"role": "mentor"},
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 200
    assert r.json()["role"] == "mentor"

    assert (
        client.put(
            f"/admin/users/{sid}/role",
            json={"role": "student"},
            headers=_auth_headers(m_token),
        ).status_code
        == 403
    )
    assert (
        client.put(
            "/admin/users/nobody/role",
            json={"role": "student"},
            headers=_auth_headers(a_token),
        ).status_code
        == 404
    )


def test_reset_password_admin_only(client: TestClient) -> None:
    a_token, _ = _create_user(client, "admin1", "pw", "admin")
    m_token, _ = _create_user(client, "mentor1", "pw", "mentor")
    s_token, sid = _make_student(client, "student1", "oldpw")
    r = client.put(
        f"/admin/users/{sid}/password",
        json={"password": "newpw"},
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 200
    login = client.post("/auth/login", json={"username": "student1", "password": "newpw"})
    assert login.status_code == 200

    assert (
        client.put(
            f"/admin/users/{sid}/password",
            json={"password": "x"},
            headers=_auth_headers(m_token),
        ).status_code
        == 403
    )
    assert (
        client.put(
            "/admin/users/nobody/password",
            json={"password": "x"},
            headers=_auth_headers(a_token),
        ).status_code
        == 404
    )


def test_delete_user_admin_only(client: TestClient) -> None:
    a_token, _ = _create_user(client, "admin1", "pw", "admin")
    m_token, _ = _create_user(client, "mentor1", "pw", "mentor")
    s_token, sid = _make_student(client, "student1", "pw")

    from ego_server.db import get_connection

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO progress "
            "(student_id, task_id, version, status, attempts, "
            "passed_tests, total_tests, last_run_at) "
            "VALUES (?, 'F1', '1.0.0', 'passed', 1, 3, 3, datetime('now'))",
            (sid,),
        )
        conn.execute(
            "INSERT INTO runs "
            "(id, student_id, task_id, version, solution_hash, status, log, created_at) "
            "VALUES ('r1', ?, 'F1', '1.0.0', 'h', 'passed', 'ok', datetime('now'))",
            (sid,),
        )
        conn.commit()
    finally:
        conn.close()

    assert client.delete(f"/admin/users/{sid}", headers=_auth_headers(m_token)).status_code == 403

    r = client.delete(f"/admin/users/{sid}", headers=_auth_headers(a_token))
    assert r.status_code == 204
    assert r.text == ""

    conn = get_connection()
    try:
        assert conn.execute("SELECT 1 FROM students WHERE id = ?", (sid,)).fetchone() is None
        assert (
            conn.execute("SELECT 1 FROM progress WHERE student_id = ?", (sid,)).fetchone() is None
        )
        assert conn.execute("SELECT 1 FROM runs WHERE student_id = ?", (sid,)).fetchone() is None
    finally:
        conn.close()


# === GET /admin/overview ===


def _insert_sync_log_row(
    *,
    status: str = "success",
    added: int = 1,
    source: str = "manual",
    repo_url: str = "file://test",
) -> None:
    from ego_server.db import get_connection

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO sync_log "
            "(started_at, finished_at, source, repo_url, git_sha, status, "
            " added, updated, skipped, errors, error_details) "
            "VALUES (datetime('now'), datetime('now'), ?, ?, NULL, ?, ?, 0, 0, 0, '')",
            (source, repo_url, status, added),
        )
        conn.commit()
    finally:
        conn.close()


def test_overview_unauthorized(client: TestClient) -> None:
    assert client.get("/admin/overview").status_code == 401


def test_overview_forbidden_for_student(client: TestClient) -> None:
    s_token, _ = _make_student(client)
    r = client.get("/admin/overview", headers=_auth_headers(s_token))
    assert r.status_code == 403


def test_overview_empty_db_latest_sync_null(client: TestClient) -> None:
    m_token, _ = _create_user(client, "mentor1", "pw", "mentor")
    r = client.get("/admin/overview", headers=_auth_headers(m_token))
    assert r.status_code == 200
    data = r.json()
    assert data["server"] == "ok"
    assert data["counts"] == {"projects": 0, "folders": 0, "tasks": 0, "students": 0}
    assert data["latest_sync"] is None


def test_overview_mentor_and_admin_success(client: TestClient) -> None:
    # Seed: 1 project, 1 folder, 1 task, 2 students (1 created via helper).
    from ego_server.db import get_connection

    conn = get_connection()
    try:
        conn.execute(
            'INSERT INTO projects (id, name, description, version, "order", '
            "default_locale, tags, version_policy, created_at, updated_at) "
            "VALUES ('p1', 'P1', '', '1.0.0', 0, 'ru', '[]', 'declare', "
            "datetime('now'), datetime('now'))"
        )
        conn.execute(
            "INSERT INTO folders (id, project_id, code, name, description, "
            '"order", level, created_at, updated_at) '
            "VALUES ('f1', 'p1', 'F', 'F1', '', 0, 'easy', "
            "datetime('now'), datetime('now'))"
        )
        conn.execute(
            "INSERT INTO tasks (id, block, slug, task_id, title, level, tags, "
            "version, content_hash, breaking, md_path, folder_id, project_id, "
            "created_at, updated_at) "
            "VALUES ('F1', 'F', 'block_f_simple', 'F1', 'T', 'easy', '[]', "
            "'1.0.0', 'h', 0, 'docs/tasks/F1.md', 'f1', 'p1', "
            "datetime('now'), datetime('now'))"
        )
        conn.commit()
    finally:
        conn.close()

    _make_student(client, "student_a")
    _make_student(client, "student_b")
    _insert_sync_log_row(status="success", added=1)

    m_token, _ = _create_user(client, "mentor1", "pw", "mentor")
    r = client.get("/admin/overview", headers=_auth_headers(m_token))
    assert r.status_code == 200
    data = r.json()
    assert data["server"] == "ok"
    assert data["counts"] == {
        "projects": 1,
        "folders": 1,
        "tasks": 1,
        "students": 2,
    }
    assert data["latest_sync"] is not None
    assert data["latest_sync"]["status"] == "success"
    assert data["latest_sync"]["added"] == 1

    a_token, _ = _create_user(client, "admin1", "pw", "admin")
    r = client.get("/admin/overview", headers=_auth_headers(a_token))
    assert r.status_code == 200
    assert r.json()["counts"]["tasks"] == 1


def test_overview_latest_sync_is_newest_row(client: TestClient) -> None:
    _insert_sync_log_row(status="success", added=1)
    _insert_sync_log_row(status="failed", added=0)

    a_token, _ = _create_user(client, "admin1", "pw", "admin")
    r = client.get("/admin/overview", headers=_auth_headers(a_token))
    assert r.status_code == 200
    latest = r.json()["latest_sync"]
    assert latest is not None
    assert latest["status"] == "failed"  # newest row wins


# === GET /admin/catalog ===


def _insert_catalog_rows() -> None:
    """Seed a deterministic 2-project / 2-folder / 2-task hierarchy.

    Layout (order is intentionally reversed from id to verify sort):

        p1 Alpha (order 0, version 2.0.0)
          f1 FolderF (order 0, easy)
            F1 First  (md_path docs/tasks/F1.md, breaking=0)
            F2 Second (md_path docs/tasks/F2.md, breaking=1)
          f2 Gamma (order 1, medium)
        p2 Beta (order 1, version 1.0.0)
          f3 Delta (order 0, hard)
            F3 Third (md_path docs/tasks/F3.md, breaking=0)
    """
    from ego_server.db import get_connection

    conn = get_connection()
    try:
        conn.execute(
            'INSERT INTO projects (id, name, description, version, "order", '
            "default_locale, tags, version_policy, created_at, updated_at) "
            "VALUES ('p2', 'Beta', '', '1.0.0', 1, 'ru', '[]', 'declare', "
            "datetime('now'), datetime('now'))"
        )
        conn.execute(
            'INSERT INTO projects (id, name, description, version, "order", '
            "default_locale, tags, version_policy, created_at, updated_at) "
            "VALUES ('p1', 'Alpha', '', '2.0.0', 0, 'ru', '[]', 'declare', "
            "datetime('now'), datetime('now'))"
        )
        conn.execute(
            "INSERT INTO folders (id, project_id, code, name, description, "
            '"order", level, created_at, updated_at) '
            "VALUES ('f2', 'p1', 'G', 'Gamma', '', 1, 'medium', "
            "datetime('now'), datetime('now'))"
        )
        conn.execute(
            "INSERT INTO folders (id, project_id, code, name, description, "
            '"order", level, created_at, updated_at) '
            "VALUES ('f1', 'p1', 'F', 'FolderF', '', 0, 'easy', "
            "datetime('now'), datetime('now'))"
        )
        conn.execute(
            "INSERT INTO folders (id, project_id, code, name, description, "
            '"order", level, created_at, updated_at) '
            "VALUES ('f3', 'p2', 'D', 'Delta', '', 0, 'hard', "
            "datetime('now'), datetime('now'))"
        )
        conn.execute(
            "INSERT INTO tasks (id, block, slug, task_id, title, level, tags, "
            "version, content_hash, breaking, md_path, folder_id, project_id, "
            "created_at, updated_at) "
            "VALUES ('F2', 'F', 'block_f_simple', 'F2', 'Second', 'easy', '[]', "
            "'1.0.0', 'h2', 1, 'docs/tasks/F2.md', 'f1', 'p1', "
            "datetime('now'), datetime('now'))"
        )
        conn.execute(
            "INSERT INTO tasks (id, block, slug, task_id, title, level, tags, "
            "version, content_hash, breaking, md_path, folder_id, project_id, "
            "created_at, updated_at) "
            "VALUES ('F1', 'F', 'block_f_simple', 'F1', 'First', 'easy', '[]', "
            "'1.0.0', 'h1', 0, 'docs/tasks/F1.md', 'f1', 'p1', "
            "datetime('now'), datetime('now'))"
        )
        conn.execute(
            "INSERT INTO tasks (id, block, slug, task_id, title, level, tags, "
            "version, content_hash, breaking, md_path, folder_id, project_id, "
            "created_at, updated_at) "
            "VALUES ('F3', 'D', 'block_d', 'F3', 'Third', 'hard', '[]', "
            "'1.0.0', 'h3', 0, 'docs/tasks/F3.md', 'f3', 'p2', "
            "datetime('now'), datetime('now'))"
        )
        conn.commit()
    finally:
        conn.close()


def test_catalog_unauthorized(client: TestClient) -> None:
    assert client.get("/admin/catalog").status_code == 401


def test_catalog_forbidden_for_student(client: TestClient) -> None:
    s_token, _ = _make_student(client)
    r = client.get("/admin/catalog", headers=_auth_headers(s_token))
    assert r.status_code == 403


def test_catalog_empty_db(client: TestClient) -> None:
    m_token, _ = _create_user(client, "mentor1", "pw", "mentor")
    r = client.get("/admin/catalog", headers=_auth_headers(m_token))
    assert r.status_code == 200
    assert r.json() == {"projects": []}


def test_catalog_hierarchy_shape_and_ordering(client: TestClient) -> None:
    _insert_catalog_rows()
    m_token, _ = _create_user(client, "mentor1", "pw", "mentor")
    r = client.get("/admin/catalog", headers=_auth_headers(m_token))
    assert r.status_code == 200
    data = r.json()

    # Projects ordered by (order, id): p1 (0) before p2 (1).
    assert [p["id"] for p in data["projects"]] == ["p1", "p2"]
    p1, p2 = data["projects"]

    # Project metadata: only existing columns exposed.
    assert p1["id"] == "p1"
    assert p1["name"] == "Alpha"
    assert p1["order"] == 0
    assert p1["version"] == "2.0.0"

    # Folders under p1 ordered by (order, id): f1 (0) before f2 (1).
    assert [f["id"] for f in p1["folders"]] == ["f1", "f2"]
    f1, f2 = p1["folders"]
    assert f1["code"] == "F"
    assert f1["name"] == "FolderF"
    assert f1["order"] == 0
    assert f1["level"] == "easy"
    assert f1["project_id"] == "p1"

    # Tasks under f1 ordered by (task_id, id): F1 before F2.
    assert [t["task_id"] for t in f1["tasks"]] == ["F1", "F2"]
    t1, t2 = f1["tasks"]
    assert t1["id"] == "F1"
    assert t1["title"] == "First"
    assert t1["level"] == "easy"
    assert t1["version"] == "1.0.0"
    assert t1["md_path"] == "docs/tasks/F1.md"
    assert t1["breaking"] is False
    assert t1["folder_id"] == "f1"
    assert t1["project_id"] == "p1"
    assert t2["breaking"] is True

    # f2 has no tasks.
    assert f2["tasks"] == []

    # p2 has one folder with one task.
    assert [f["id"] for f in p2["folders"]] == ["f3"]
    assert [t["task_id"] for t in p2["folders"][0]["tasks"]] == ["F3"]


def test_catalog_admin_allowed(client: TestClient) -> None:
    _insert_catalog_rows()
    a_token, _ = _create_user(client, "admin1", "pw", "admin")
    r = client.get("/admin/catalog", headers=_auth_headers(a_token))
    assert r.status_code == 200
    assert len(r.json()["projects"]) == 2


def test_catalog_search_prunes_unmatched_tasks(client: TestClient) -> None:
    _insert_catalog_rows()
    a_token, _ = _create_user(client, "admin1", "pw", "admin")
    r = client.get("/admin/catalog?q=Second", headers=_auth_headers(a_token))
    assert r.status_code == 200
    projects = r.json()["projects"]
    # Only p1 retained (ancestor of the matching task's folder).
    assert [p["id"] for p in projects] == ["p1"]
    p1 = projects[0]
    # Only f1 retained (ancestor of the matching task).
    assert [f["id"] for f in p1["folders"]] == ["f1"]
    f1 = p1["folders"][0]
    # Only the matching task retained; sibling pruned.
    assert [t["task_id"] for t in f1["tasks"]] == ["F2"]


def test_catalog_search_prunes_unmatched_folders(client: TestClient) -> None:
    _insert_catalog_rows()
    a_token, _ = _create_user(client, "admin1", "pw", "admin")
    # Match folder f2 by name "Gamma"; no tasks under it, so it stays empty.
    r = client.get("/admin/catalog?q=Gamma", headers=_auth_headers(a_token))
    assert r.status_code == 200
    projects = r.json()["projects"]
    assert [p["id"] for p in projects] == ["p1"]
    p1 = projects[0]
    assert [f["id"] for f in p1["folders"]] == ["f2"]
    assert p1["folders"][0]["tasks"] == []


def test_catalog_search_keeps_project_subtree(client: TestClient) -> None:
    _insert_catalog_rows()
    a_token, _ = _create_user(client, "admin1", "pw", "admin")
    # Match project p2 by name "Beta"; all its folders/tasks retained.
    r = client.get("/admin/catalog?q=Beta", headers=_auth_headers(a_token))
    assert r.status_code == 200
    projects = r.json()["projects"]
    assert [p["id"] for p in projects] == ["p2"]
    p2 = projects[0]
    assert [f["id"] for f in p2["folders"]] == ["f3"]
    assert [t["task_id"] for t in p2["folders"][0]["tasks"]] == ["F3"]


def test_catalog_search_case_insensitive(client: TestClient) -> None:
    _insert_catalog_rows()
    a_token, _ = _create_user(client, "admin1", "pw", "admin")
    r = client.get("/admin/catalog?q=fIrSt", headers=_auth_headers(a_token))
    assert r.status_code == 200
    tasks = r.json()["projects"][0]["folders"][0]["tasks"]
    assert [t["task_id"] for t in tasks] == ["F1"]


def test_catalog_search_matches_task_md_path(client: TestClient) -> None:
    _insert_catalog_rows()
    a_token, _ = _create_user(client, "admin1", "pw", "admin")
    r = client.get("/admin/catalog?q=docs/tasks/F3.md", headers=_auth_headers(a_token))
    assert r.status_code == 200
    projects = r.json()["projects"]
    assert [p["id"] for p in projects] == ["p2"]
    assert projects[0]["folders"][0]["tasks"][0]["task_id"] == "F3"


def test_catalog_search_no_match_returns_empty(client: TestClient) -> None:
    _insert_catalog_rows()
    a_token, _ = _create_user(client, "admin1", "pw", "admin")
    r = client.get("/admin/catalog?q=zzznomatch", headers=_auth_headers(a_token))
    assert r.status_code == 200
    assert r.json() == {"projects": []}


# === GET /admin/tasks/{task_id}/studio ===


@pytest.fixture
def studio_env(tmp_path, monkeypatch):
    """Build a local content repo + DB task row + TestClient.

    Creates ``<tmp>/repo/tasks/task_f1.md`` with ``.solution.py`` and
    ``.tests.py`` sidecars, points ``EGO_TASKS_REPO_URL`` at the repo,
    reloads ``content_config`` so the singleton picks up the env, and
    inserts a matching ``tasks`` row whose ``md_path`` is relative to
    the repo root.
    """
    repo = tmp_path / "repo"
    tasks_dir = repo / "tasks"
    tasks_dir.mkdir(parents=True)
    (tasks_dir / "task_f1.md").write_text(
        "# Задача F1: Studio\n\n## Условие\nDo the thing.\n",
        encoding="utf-8",
    )
    (tasks_dir / "task_f1.solution.py").write_text(
        "def task_f1():\n    return 42\n",
        encoding="utf-8",
    )
    (tasks_dir / "task_f1.tests.py").write_text(
        "from solution import task_f1\n\n@case\ndef t():\n    assert task_f1() == 42\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("EGO_DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("EGO_TASKS_REPO_URL", str(repo))

    import ego_server.config
    import ego_server.content_config
    import ego_server.db

    importlib.reload(ego_server.config)
    importlib.reload(ego_server.content_config)
    importlib.reload(ego_server.db)

    from ego_server.db import init_db

    init_db()

    from ego_server.db import get_connection

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO tasks (id, block, slug, task_id, title, level, tags, "
            "version, content_hash, breaking, md_path, folder_id, project_id, "
            "created_at, updated_at) "
            "VALUES ('F1', 'F', 'block_f_simple', 'F1', 'Studio', 'easy', '[]', "
            "'1.0.0', 'h', 0, 'tasks/task_f1.md', NULL, NULL, "
            "datetime('now'), datetime('now'))"
        )
        conn.commit()
    finally:
        conn.close()

    import ego_server.main

    importlib.reload(ego_server.main)
    from ego_server.main import app

    with TestClient(app) as c:
        yield c


def _insert_task_row(
    *,
    task_id: str = "F1",
    md_path: str = "tasks/task_f1.md",
    version: str = "1.0.0",
) -> None:
    from ego_server.db import get_connection

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO tasks (id, block, slug, task_id, title, level, tags, "
            "version, content_hash, breaking, md_path, folder_id, project_id, "
            "created_at, updated_at) "
            "VALUES (?, 'F', 'block_f_simple', ?, 'Studio', 'easy', '[]', "
            "?, 'h', 0, ?, NULL, NULL, datetime('now'), datetime('now'))",
            (task_id, task_id, version, md_path),
        )
        conn.commit()
    finally:
        conn.close()


def test_studio_unauthorized(studio_env: TestClient) -> None:
    assert studio_env.get("/admin/tasks/F1/studio").status_code == 401


def test_studio_forbidden_for_student(studio_env: TestClient) -> None:
    s_token, _ = _make_student(studio_env)
    r = studio_env.get("/admin/tasks/F1/studio", headers=_auth_headers(s_token))
    assert r.status_code == 403


def test_studio_mentor_and_admin_read(studio_env: TestClient) -> None:
    m_token, _ = _create_user(studio_env, "mentor1", "pw", "mentor")
    r = studio_env.get("/admin/tasks/F1/studio", headers=_auth_headers(m_token))
    assert r.status_code == 200
    data = r.json()
    assert data["task_id"] == "F1"
    assert data["version"] == "1.0.0"
    assert data["md_path"] == "tasks/task_f1.md"
    assert "# Задача F1" in data["markdown"]
    assert "def task_f1" in data["solution_py"]
    assert "assert task_f1() == 42" in data["tests_py"]
    assert data["writable"] is True
    assert data["read_only_reason"] == ""

    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.get("/admin/tasks/F1/studio", headers=_auth_headers(a_token))
    assert r.status_code == 200
    assert r.json()["markdown"]


def test_studio_missing_tests_sidecar_returns_empty(studio_env: TestClient) -> None:
    from ego_server.content_config import content_settings

    repo = content_settings.to_config().resolved_local_path
    (repo / "tasks" / "task_f1.tests.py").unlink()

    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.get("/admin/tasks/F1/studio", headers=_auth_headers(a_token))
    assert r.status_code == 200
    data = r.json()
    assert data["tests_py"] == ""
    assert data["solution_py"]  # solution still present
    assert data["writable"] is True


def test_studio_unconfigured_reports_read_only(tmp_path, monkeypatch) -> None:
    # No EGO_TASKS_REPO_URL configured → read-only with "not configured".
    monkeypatch.setenv("EGO_DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.delenv("EGO_TASKS_REPO_URL", raising=False)

    import ego_server.config
    import ego_server.content_config
    import ego_server.db

    importlib.reload(ego_server.config)
    importlib.reload(ego_server.content_config)
    importlib.reload(ego_server.db)
    from ego_server.db import init_db

    init_db()
    _insert_task_row()

    import ego_server.main

    importlib.reload(ego_server.main)
    from ego_server.main import app

    with TestClient(app) as c:
        a_token, _ = _create_user(c, "admin1", "pw", "admin")
        r = c.get("/admin/tasks/F1/studio", headers=_auth_headers(a_token))
        assert r.status_code == 200
        data = r.json()
        assert data["writable"] is False
        assert "not configured" in data["read_only_reason"]
        assert data["markdown"] == ""
        assert data["solution_py"] == ""


def test_studio_root_nonexistent_reports_read_only(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("EGO_DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("EGO_TASKS_REPO_URL", str(tmp_path / "missing"))

    import ego_server.config
    import ego_server.content_config
    import ego_server.db

    importlib.reload(ego_server.config)
    importlib.reload(ego_server.content_config)
    importlib.reload(ego_server.db)
    from ego_server.db import init_db

    init_db()
    _insert_task_row()

    import ego_server.main

    importlib.reload(ego_server.main)
    from ego_server.main import app

    with TestClient(app) as c:
        a_token, _ = _create_user(c, "admin1", "pw", "admin")
        r = c.get("/admin/tasks/F1/studio", headers=_auth_headers(a_token))
        assert r.status_code == 200
        data = r.json()
        assert data["writable"] is False
        assert "not found" in data["read_only_reason"]
        assert data["markdown"] == ""


def test_studio_unwritable_reports_read_only(studio_env: TestClient) -> None:
    import os

    from ego_server.content_config import content_settings

    repo = content_settings.to_config().resolved_local_path
    mode = os.stat(repo).st_mode
    os.chmod(repo, 0o555)
    try:
        if os.access(repo, os.W_OK):
            pytest.skip("platform does not honour directory write bits")
        a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
        r = studio_env.get("/admin/tasks/F1/studio", headers=_auth_headers(a_token))
        assert r.status_code == 200
        data = r.json()
        assert data["writable"] is False
        assert "not writable" in data["read_only_reason"]
        # Content is still safely readable.
        assert data["markdown"]
        assert data["solution_py"]
    finally:
        os.chmod(repo, mode)


def test_studio_tampered_traversal_blocked(studio_env: TestClient) -> None:
    # Tamper the DB row so md_path escapes the root via '..'.
    from ego_server.db import get_connection

    conn = get_connection()
    try:
        conn.execute("UPDATE tasks SET md_path = ? WHERE id = 'F1'", ("../secret.md",))
        conn.commit()
    finally:
        conn.close()

    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.get("/admin/tasks/F1/studio", headers=_auth_headers(a_token))
    assert r.status_code == 200
    data = r.json()
    assert data["writable"] is False
    assert "escapes" in data["read_only_reason"]
    assert data["markdown"] == ""
    assert data["solution_py"] == ""


def test_studio_symlink_escape_blocked(studio_env: TestClient) -> None:
    import os

    from ego_server.content_config import content_settings

    repo = content_settings.to_config().resolved_local_path
    outside = repo.parent / "outside_target.py"
    outside.write_text("STOLEN\n", encoding="utf-8")
    sol_link = repo / "tasks" / "task_f1.solution.py"
    sol_link.unlink()
    try:
        os.symlink(outside, sol_link)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not supported on this platform")

    try:
        a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
        r = studio_env.get("/admin/tasks/F1/studio", headers=_auth_headers(a_token))
        assert r.status_code == 200
        data = r.json()
        assert data["writable"] is False
        assert "escapes" in data["read_only_reason"]
        # Markdown is still safely readable; the escaping sidecar is not.
        assert data["markdown"]
        assert data["solution_py"] == ""
        assert "STOLEN" not in data["solution_py"]
    finally:
        try:
            sol_link.unlink()
        except OSError:
            pass


def test_studio_missing_markdown_404(studio_env: TestClient) -> None:
    from ego_server.content_config import content_settings

    repo = content_settings.to_config().resolved_local_path
    (repo / "tasks" / "task_f1.md").unlink()

    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.get("/admin/tasks/F1/studio", headers=_auth_headers(a_token))
    assert r.status_code == 404


def test_studio_missing_solution_409(studio_env: TestClient) -> None:
    from ego_server.content_config import content_settings

    repo = content_settings.to_config().resolved_local_path
    (repo / "tasks" / "task_f1.solution.py").unlink()

    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.get("/admin/tasks/F1/studio", headers=_auth_headers(a_token))
    assert r.status_code == 409


def test_studio_task_not_found_404(studio_env: TestClient) -> None:
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.get("/admin/tasks/NOPE/studio", headers=_auth_headers(a_token))
    assert r.status_code == 404
