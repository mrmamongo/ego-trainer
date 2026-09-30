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
    r = client.get("/")
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


def test_only_mentor_can_appoint_mentor(client: TestClient) -> None:
    a_token, _ = _create_user(client, "admin1", "pw", "admin")
    m_token, _ = _create_user(client, "mentor1", "pw", "mentor")
    s_token, sid = _make_student(client, "student1")
    r = client.put(
        f"/admin/users/{sid}/role",
        json={"role": "mentor"},
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 403
    r = client.put(
        f"/admin/users/{sid}/role", json={"role": "mentor"}, headers=_auth_headers(m_token)
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
            f"/admin/users/{sid}/password", json={"password": "x"}, headers=_auth_headers(m_token)
        ).status_code
        == 403
    )
    assert (
        client.put(
            "/admin/users/nobody/password", json={"password": "x"}, headers=_auth_headers(a_token)
        ).status_code
        == 404
    )


def test_mentor_promotion_rejects_other_privileges_and_stale_roles(client: TestClient):
    mentor, mentor_id = _create_user(client, "mentor", "pw", "mentor")
    admin, admin_id = _create_user(client, "admin", "pw", "admin")
    student, student_id = _make_student(client, "learner")
    endpoint = f"/admin/users/{student_id}/role"
    assert (
        client.put(endpoint, json={"role": "mentor"}, headers=_auth_headers(student)).status_code
        == 403
    )
    assert (
        client.put(endpoint, json={"role": "admin"}, headers=_auth_headers(mentor)).status_code
        == 403
    )
    assert (
        client.put(
            f"/admin/users/{admin_id}/role", json={"role": "mentor"}, headers=_auth_headers(mentor)
        ).status_code
        == 409
    )
    assert (
        client.post(
            "/admin/users",
            json={"username": "bypass", "password": "p", "role": "mentor"},
            headers=_auth_headers(admin),
        ).status_code
        == 403
    )
    from ego_server.db import get_connection

    conn = get_connection()
    try:
        conn.execute("UPDATE students SET role='student' WHERE id=?", (mentor_id,))
        conn.commit()
        assert (
            client.put(endpoint, json={"role": "mentor"}, headers=_auth_headers(mentor)).status_code
            == 403
        )
        conn.execute("UPDATE students SET role='mentor' WHERE id=?", (mentor_id,))
        conn.commit()
        assert (
            client.put(endpoint, json={"role": "mentor"}, headers=_auth_headers(mentor)).status_code
            == 200
        )
        grant = conn.execute("SELECT actor_id,user_id FROM mentor_grants").fetchone()
        assert tuple(grant) == (mentor_id, student_id)
        assert (
            client.put(endpoint, json={"role": "mentor"}, headers=_auth_headers(mentor)).status_code
            == 409
        )
    finally:
        conn.close()


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


def _insert_shared_folder_id_rows() -> None:
    """Seed two projects that both use folder id ``shared``.

    The ``folders`` table has PRIMARY KEY (id, project_id), so the same
    folder id may legitimately appear under more than one project. This
    fixture stresses that case:

        projA (order 0)
          shared (code A, name AlphaFolder)
            TA AlphaTask  (md_path docs/tasks/TA.md)
        projB (order 1)
          shared (code B, name BetaFolder)
            TB BetaTask  (md_path docs/tasks/TB.md)
    """
    from ego_server.db import get_connection

    conn = get_connection()
    try:
        conn.execute(
            'INSERT INTO projects (id, name, description, version, "order", '
            "default_locale, tags, version_policy, created_at, updated_at) "
            "VALUES ('projA', 'Alpha', '', '1.0.0', 0, 'ru', '[]', 'declare', "
            "datetime('now'), datetime('now'))"
        )
        conn.execute(
            'INSERT INTO projects (id, name, description, version, "order", '
            "default_locale, tags, version_policy, created_at, updated_at) "
            "VALUES ('projB', 'Beta', '', '1.0.0', 1, 'ru', '[]', 'declare', "
            "datetime('now'), datetime('now'))"
        )
        for pid, code, name in (("projA", "A", "AlphaFolder"), ("projB", "B", "BetaFolder")):
            conn.execute(
                "INSERT INTO folders (id, project_id, code, name, description, "
                '"order", level, created_at, updated_at) '
                "VALUES ('shared', ?, ?, ?, '', 0, 'easy', "
                "datetime('now'), datetime('now'))",
                (pid, code, name),
            )
        conn.execute(
            "INSERT INTO tasks (id, block, slug, task_id, title, level, tags, "
            "version, content_hash, breaking, md_path, folder_id, project_id, "
            "created_at, updated_at) "
            "VALUES ('TA', 'A', 'block_a', 'TA', 'AlphaTask', 'easy', '[]', "
            "'1.0.0', 'hA', 0, 'docs/tasks/TA.md', 'shared', 'projA', "
            "datetime('now'), datetime('now'))"
        )
        conn.execute(
            "INSERT INTO tasks (id, block, slug, task_id, title, level, tags, "
            "version, content_hash, breaking, md_path, folder_id, project_id, "
            "created_at, updated_at) "
            "VALUES ('TB', 'B', 'block_b', 'TB', 'BetaTask', 'easy', '[]', "
            "'1.0.0', 'hB', 0, 'docs/tasks/TB.md', 'shared', 'projB', "
            "datetime('now'), datetime('now'))"
        )
        conn.commit()
    finally:
        conn.close()


def test_catalog_shared_folder_id_no_cross_leak_unfiltered(client: TestClient) -> None:
    """Two projects sharing folder id ``shared`` must not mix tasks.

    Regression: folder-related maps were keyed by ``folder_id`` alone, so
    tasks from project A's ``shared`` folder leaked into project B's
    ``shared`` folder (and vice versa) in the unfiltered catalog output.
    Each folder must contain only its own project's task.
    """
    _insert_shared_folder_id_rows()
    a_token, _ = _create_user(client, "admin1", "pw", "admin")
    r = client.get("/admin/catalog", headers=_auth_headers(a_token))
    assert r.status_code == 200
    projects = r.json()["projects"]
    assert [p["id"] for p in projects] == ["projA", "projB"]

    by_id = {p["id"]: p for p in projects}
    # Each project has exactly one folder, both with id "shared".
    assert [f["id"] for f in by_id["projA"]["folders"]] == ["shared"]
    assert [f["id"] for f in by_id["projB"]["folders"]] == ["shared"]

    # The crucial regression check: no cross-project task leakage.
    a_tasks = by_id["projA"]["folders"][0]["tasks"]
    b_tasks = by_id["projB"]["folders"][0]["tasks"]
    assert [t["task_id"] for t in a_tasks] == ["TA"]
    assert [t["task_id"] for t in b_tasks] == ["TB"]
    # Folder metadata is per-project, not merged.
    assert by_id["projA"]["folders"][0]["code"] == "A"
    assert by_id["projA"]["folders"][0]["name"] == "AlphaFolder"
    assert by_id["projB"]["folders"][0]["code"] == "B"
    assert by_id["projB"]["folders"][0]["name"] == "BetaFolder"


def test_catalog_shared_folder_id_search_does_not_leak_other_project(
    client: TestClient,
) -> None:
    """Searching for project A's task must not retain project B via the
    shared folder id.

    Regression: ``folder_has_match_task`` was keyed by ``folder_id`` alone,
    so a task hit in project A's ``shared`` folder marked project B's
    ``shared`` folder as having a matching task, keeping project B (and
    its non-matching task) in the filtered output. Project B must be
    fully pruned when only project A's task matches.
    """
    _insert_shared_folder_id_rows()
    a_token, _ = _create_user(client, "admin1", "pw", "admin")
    r = client.get("/admin/catalog?q=AlphaTask", headers=_auth_headers(a_token))
    assert r.status_code == 200
    projects = r.json()["projects"]
    # Only projA retained; projB must NOT leak through the shared folder id.
    assert [p["id"] for p in projects] == ["projA"]
    p = projects[0]
    assert [f["id"] for f in p["folders"]] == ["shared"]
    assert [t["task_id"] for t in p["folders"][0]["tasks"]] == ["TA"]

    # Symmetric check: searching for project B's task keeps only projB.
    r = client.get("/admin/catalog?q=BetaTask", headers=_auth_headers(a_token))
    assert r.status_code == 200
    projects = r.json()["projects"]
    assert [p["id"] for p in projects] == ["projB"]
    p = projects[0]
    assert [f["id"] for f in p["folders"]] == ["shared"]
    assert [t["task_id"] for t in p["folders"][0]["tasks"]] == ["TB"]


# === GET /admin/tasks/{task_id}/studio ===


# Relative path (from repo root) to the studio fixture's task folder.
# Used by helpers/tests that read or mutate canonical files on disk.
_STUDIO_FOLDER_REL = "projects/p1/folders/f1"
_STUDIO_MD_PATH = f"{_STUDIO_FOLDER_REL}/task_f1.md"


@pytest.fixture
def studio_env(tmp_path, monkeypatch):
    """Build a local catalog-mode content repo + DB rows + TestClient.

    Creates a valid ADR-0016 D16.6 catalog layout so the production
    admin router's DB + canonical ``discover_repo`` writability
    cross-check agrees on an existing ``declare`` project for task F1::

        <tmp>/repo/
        ├── catalog.yaml                 # points to projects/p1
        └── projects/
            └── p1/
                ├── project.yaml         # id p1, version_policy declare
                └── folders/
                    └── f1/
                        ├── folder.yaml   # id f1
                        ├── task_f1.md    # frontmatter id F1, version 1.0.0
                        ├── task_f1.solution.py
                        └── task_f1.tests.py

    Points ``EGO_TASKS_REPO_URL`` at the repo, reloads ``content_config``
    so the singleton picks up the env, and inserts matching ``projects``,
    ``folders``, and ``tasks`` rows whose ``md_path`` is relative to the
    repo root and matches the canonical discovery path exactly.
    """
    repo = tmp_path / "repo"
    proj_dir = repo / "projects" / "p1"
    folder_dir = proj_dir / "folders" / "f1"
    folder_dir.mkdir(parents=True)

    (repo / "catalog.yaml").write_text(
        "schema_version: 1\nprojects:\n  - id: p1\n    path: projects/p1\n",
        encoding="utf-8",
    )
    (proj_dir / "project.yaml").write_text(
        "id: p1\nname: P1\nversion: '1.0.0'\nversion_policy: declare\n",
        encoding="utf-8",
    )
    (folder_dir / "folder.yaml").write_text(
        "id: f1\ncode: F\nname: F1\nlevel: easy\n",
        encoding="utf-8",
    )
    (folder_dir / "task_f1.md").write_text(
        "---\n"
        "id: F1\n"
        "title: Studio\n"
        "version: '1.0.0'\n"
        "level: easy\n"
        "---\n\n"
        "# Задача F1: Studio\n\n## Условие\nDo the thing.\n",
        encoding="utf-8",
    )
    (folder_dir / "task_f1.solution.py").write_text(
        "def task_f1():\n    return 42\n",
        encoding="utf-8",
    )
    (folder_dir / "task_f1.tests.py").write_text(
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
            "VALUES ('F1', 'F', 'block_f_simple', 'F1', 'Studio', 'easy', '[]', "
            "'1.0.0', 'h', 0, ?, 'f1', 'p1', "
            "datetime('now'), datetime('now'))",
            (_STUDIO_MD_PATH,),
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
    md_path: str = _STUDIO_MD_PATH,
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
    assert data["md_path"] == _STUDIO_MD_PATH
    assert "# Задача F1" in data["markdown"]
    assert "def task_f1" in data["solution_py"]
    assert "assert task_f1() == 42" in data["tests_py"]
    assert data["content_etag"]  # non-empty etag for writable, contained task
    assert data["version_policy"] == "declare"
    assert data["writable"] is True
    assert data["read_only_reason"] == ""

    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.get("/admin/tasks/F1/studio", headers=_auth_headers(a_token))
    assert r.status_code == 200
    assert r.json()["markdown"]


def test_studio_missing_tests_sidecar_returns_empty(studio_env: TestClient) -> None:
    from ego_server.content_config import content_settings

    repo = content_settings.to_config().resolved_local_path
    (repo / _STUDIO_FOLDER_REL / "task_f1.tests.py").unlink()

    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.get("/admin/tasks/F1/studio", headers=_auth_headers(a_token))
    assert r.status_code == 200
    data = r.json()
    assert data["tests_py"] == ""
    assert data["solution_py"]  # solution still present
    assert data["writable"] is True
    # Etag is still returned — missing optional tests encoded as explicit missing state.
    assert data["content_etag"]


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
    sol_link = repo / _STUDIO_FOLDER_REL / "task_f1.solution.py"
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
    (repo / _STUDIO_FOLDER_REL / "task_f1.md").unlink()

    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.get("/admin/tasks/F1/studio", headers=_auth_headers(a_token))
    assert r.status_code == 404


def test_studio_missing_solution_409(studio_env: TestClient) -> None:
    from ego_server.content_config import content_settings

    repo = content_settings.to_config().resolved_local_path
    (repo / _STUDIO_FOLDER_REL / "task_f1.solution.py").unlink()

    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.get("/admin/tasks/F1/studio", headers=_auth_headers(a_token))
    assert r.status_code == 409


def test_studio_task_not_found_404(studio_env: TestClient) -> None:
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.get("/admin/tasks/NOPE/studio", headers=_auth_headers(a_token))
    assert r.status_code == 404


# === Task Studio writability policy (version_policy gate) ===


def _set_project_policy(project_id: str, policy: str) -> None:
    from ego_server.db import get_connection

    conn = get_connection()
    try:
        conn.execute(
            "UPDATE projects SET version_policy = ? WHERE id = ?",
            (policy, project_id),
        )
        conn.commit()
    finally:
        conn.close()


def _set_task_project(task_id: str, project_id: str | None) -> None:
    from ego_server.db import get_connection

    conn = get_connection()
    try:
        conn.execute(
            "UPDATE tasks SET project_id = ? WHERE id = ?",
            (project_id, task_id),
        )
        conn.commit()
    finally:
        conn.close()


def test_studio_get_auto_minor_read_only(studio_env: TestClient) -> None:
    """auto_minor project → writable=False, version_policy set, content returned."""
    _set_project_policy("p1", "auto_minor")
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.get("/admin/tasks/F1/studio", headers=_auth_headers(a_token))
    assert r.status_code == 200
    data = r.json()
    assert data["writable"] is False
    assert data["version_policy"] == "auto_minor"
    assert data["read_only_reason"]  # actionable
    assert "auto_minor" in data["read_only_reason"]
    # Canonical content is still returned for browse.
    assert data["markdown"]
    assert data["solution_py"]
    assert data["tests_py"]


def test_studio_get_missing_project_read_only(studio_env: TestClient) -> None:
    """Task references a missing project → writable=False, version_policy=None."""
    _set_task_project("F1", "ghost")
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.get("/admin/tasks/F1/studio", headers=_auth_headers(a_token))
    assert r.status_code == 200
    data = r.json()
    assert data["writable"] is False
    assert data["version_policy"] is None
    assert data["read_only_reason"]
    assert "ghost" in data["read_only_reason"]
    assert data["markdown"]


def test_studio_get_legacy_null_project_read_only(studio_env: TestClient) -> None:
    """Legacy NULL project_id → writable=False, version_policy=None."""
    _set_task_project("F1", None)
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.get("/admin/tasks/F1/studio", headers=_auth_headers(a_token))
    assert r.status_code == 200
    data = r.json()
    assert data["writable"] is False
    assert data["version_policy"] is None
    assert data["read_only_reason"]
    assert "legacy" in data["read_only_reason"].lower()
    assert data["markdown"]


def test_studio_get_declare_writable(studio_env: TestClient) -> None:
    """declare project (the fixture default) → writable=True, version_policy='declare'."""
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.get("/admin/tasks/F1/studio", headers=_auth_headers(a_token))
    assert r.status_code == 200
    data = r.json()
    assert data["version_policy"] == "declare"
    assert data["writable"] is True
    assert data["read_only_reason"] == ""


# === POST /admin/tasks/{task_id}/studio/validate ===


def _valid_candidate_md(
    *, version: str = "2.0.0", task_id: str = "F1", title: str = "Studio"
) -> str:
    """Build a candidate markdown with valid YAML frontmatter + body."""
    return (
        f"---\nid: {task_id}\ntitle: '{title}'\nversion: '{version}'\nlevel: easy\n---\n\n"
        f"# Задача {task_id}: {title}\n\n## Условие\nDo the thing.\n"
    )


_VALID_SOLUTION = "def task_f1():\n    return 42\n"
_VALID_TESTS = "from solution import task_f1\n\n@case\ndef t():\n    assert task_f1() == 42\n"


def _validate_payload(
    *,
    expected_version: str = "1.0.0",
    expected_content_etag: str = "",
    markdown: str | None = None,
    solution_py: str | None = None,
    tests_py: str | None = None,
) -> dict:
    return {
        "expected_version": expected_version,
        "expected_content_etag": expected_content_etag,
        "markdown": markdown if markdown is not None else _valid_candidate_md(),
        "solution_py": solution_py if solution_py is not None else _VALID_SOLUTION,
        "tests_py": tests_py if tests_py is not None else _VALID_TESTS,
    }


def _read_canonical(studio_env: TestClient) -> dict[str, str]:
    """Read the three canonical files from the configured content repo."""
    from ego_server.content_config import content_settings

    repo = content_settings.to_config().resolved_local_path
    folder = repo / _STUDIO_FOLDER_REL
    files = {}
    for name in ("task_f1.md", "task_f1.solution.py", "task_f1.tests.py"):
        p = folder / name
        # read_bytes().decode("utf-8") preserves the exact canonical bytes
        # (no newline translation), so an unchanged candidate roundtrips to
        # the same bytes represented by content_etag — matching the
        # server's byte-exact content_changed comparison.
        files[name] = p.read_bytes().decode("utf-8") if p.is_file() else ""
    return files


def _get_studio_etag(client: TestClient, token: str, task_id: str = "F1") -> str:
    """GET the Task Studio content and return the fresh content_etag."""
    r = client.get(f"/admin/tasks/{task_id}/studio", headers=_auth_headers(token))
    assert r.status_code == 200, f"GET studio failed: {r.text}"
    etag = r.json()["content_etag"]
    assert etag, "content_etag must be non-empty for a writable, contained task"
    return etag


def test_studio_validate_unauthorized(studio_env: TestClient) -> None:
    r = studio_env.post("/admin/tasks/F1/studio/validate", json=_validate_payload())
    assert r.status_code == 401


def test_studio_validate_forbidden_for_student(studio_env: TestClient) -> None:
    s_token, _ = _make_student(studio_env)
    r = studio_env.post(
        "/admin/tasks/F1/studio/validate",
        json=_validate_payload(),
        headers=_auth_headers(s_token),
    )
    assert r.status_code == 403


def test_studio_validate_forbidden_for_mentor(studio_env: TestClient) -> None:
    m_token, _ = _create_user(studio_env, "mentor1", "pw", "mentor")
    r = studio_env.post(
        "/admin/tasks/F1/studio/validate",
        json=_validate_payload(),
        headers=_auth_headers(m_token),
    )
    assert r.status_code == 403


def test_studio_validate_admin_happy(studio_env: TestClient) -> None:
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    etag = _get_studio_etag(studio_env, a_token)
    before = _read_canonical(studio_env)
    r = studio_env.post(
        "/admin/tasks/F1/studio/validate",
        json=_validate_payload(expected_content_etag=etag),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["valid"] is True
    assert data["task_id"] == "F1"
    assert data["current_version"] == "1.0.0"
    assert data["candidate_version"] == "2.0.0"
    assert data["content_changed"] is True
    assert data["version_policy"] == "declare"
    # Canonical files must be byte-identical after validation.
    assert _read_canonical(studio_env) == before


def test_studio_validate_unchanged_content_no_bump_ok(studio_env: TestClient) -> None:
    """When content is unchanged, version need not bump (declare policy)."""
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    etag = _get_studio_etag(studio_env, a_token)
    canonical = _read_canonical(studio_env)
    # Candidate matches canonical exactly (frontmatter + body).
    payload = _validate_payload(
        expected_content_etag=etag,
        markdown=canonical["task_f1.md"],
        solution_py=canonical["task_f1.solution.py"],
        tests_py=canonical["task_f1.tests.py"],
    )
    r = studio_env.post(
        "/admin/tasks/F1/studio/validate",
        json=payload,
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["valid"] is True
    assert data["content_changed"] is False
    assert data["candidate_version"] == "1.0.0"


def test_studio_validate_malformed_frontmatter_422(studio_env: TestClient) -> None:
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    # Unclosed frontmatter.
    bad_md = "---\nid: F1\ntitle: Test\n\n# Задача F1: Test\n\n## Условие\nx\n"
    r = studio_env.post(
        "/admin/tasks/F1/studio/validate",
        json=_validate_payload(markdown=bad_md),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 422
    assert "frontmatter" in r.json()["detail"].lower()


def test_studio_validate_frontmatter_id_mismatch_422(studio_env: TestClient) -> None:
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.post(
        "/admin/tasks/F1/studio/validate",
        json=_validate_payload(markdown=_valid_candidate_md(task_id="WRONG")),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 422
    assert "does not match" in r.json()["detail"]


def test_studio_validate_invalid_semver_422(studio_env: TestClient) -> None:
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.post(
        "/admin/tasks/F1/studio/validate",
        json=_validate_payload(markdown=_valid_candidate_md(version="1.0")),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 422
    assert "semver" in r.json()["detail"].lower()


def test_studio_validate_malformed_solution_422_no_write(studio_env: TestClient) -> None:
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    before = _read_canonical(studio_env)
    r = studio_env.post(
        "/admin/tasks/F1/studio/validate",
        json=_validate_payload(solution_py="def task_f1(\n    return 42\n"),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 422
    assert "solution" in r.json()["detail"].lower()
    # Canonical files must remain byte-identical.
    assert _read_canonical(studio_env) == before


def test_studio_validate_malformed_tests_422(studio_env: TestClient) -> None:
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.post(
        "/admin/tasks/F1/studio/validate",
        json=_validate_payload(tests_py="def (\n"),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 422
    assert "tests" in r.json()["detail"].lower()


def test_studio_validate_stale_expected_version_409(studio_env: TestClient) -> None:
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.post(
        "/admin/tasks/F1/studio/validate",
        json=_validate_payload(expected_version="0.9.0"),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 409
    assert "expected_version" in r.json()["detail"]


def test_studio_validate_non_bumped_declared_version_409(studio_env: TestClient) -> None:
    """Content changed + version_policy=declare → version must be > current."""
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    etag = _get_studio_etag(studio_env, a_token)
    # Candidate version == current (1.0.0), but content differs → 409.
    r = studio_env.post(
        "/admin/tasks/F1/studio/validate",
        json=_validate_payload(
            expected_content_etag=etag,
            markdown=_valid_candidate_md(version="1.0.0", title="Changed"),
        ),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 409
    assert "declare" in r.json()["detail"]


def test_studio_validate_traversal_409(studio_env: TestClient) -> None:
    from ego_server.db import get_connection

    conn = get_connection()
    try:
        conn.execute("UPDATE tasks SET md_path = ? WHERE id = 'F1'", ("../secret.md",))
        conn.commit()
    finally:
        conn.close()

    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.post(
        "/admin/tasks/F1/studio/validate",
        json=_validate_payload(),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 409
    assert "escapes" in r.json()["detail"]


def test_studio_validate_read_only_unconfigured_409(tmp_path, monkeypatch) -> None:
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
        r = c.post(
            "/admin/tasks/F1/studio/validate",
            json=_validate_payload(),
            headers=_auth_headers(a_token),
        )
        assert r.status_code == 409
        assert "read-only" in r.json()["detail"].lower()


def test_studio_validate_task_not_found_404(studio_env: TestClient) -> None:
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.post(
        "/admin/tasks/NOPE/studio/validate",
        json=_validate_payload(),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 404


# === PUT /admin/tasks/{task_id}/studio ===


def _save_payload(
    *,
    expected_version: str = "1.0.0",
    expected_content_etag: str = "",
    markdown: str | None = None,
    solution_py: str | None = None,
    tests_py: str | None = None,
) -> dict:
    """Build a PUT /studio request body (same shape as validate)."""
    return {
        "expected_version": expected_version,
        "expected_content_etag": expected_content_etag,
        "markdown": markdown if markdown is not None else _valid_candidate_md(),
        "solution_py": solution_py if solution_py is not None else _VALID_SOLUTION,
        "tests_py": tests_py if tests_py is not None else _VALID_TESTS,
    }


def _db_task_row(task_id: str = "F1") -> dict | None:
    """Read the tasks row for ``task_id`` from the live DB."""
    from ego_server.db import get_connection

    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, task_id, version, content_hash, md_path, "
            "folder_id, project_id FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        return dict(row) if row is not None else None
    finally:
        conn.close()


def _db_task_versions(task_id: str = "F1") -> list[dict]:
    """Read all task_versions rows for ``task_id``."""
    from ego_server.db import get_connection

    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT task_id, version, content_hash, breaking, md_path "
            "FROM task_versions WHERE task_id = ? ORDER BY version",
            (task_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def _db_sync_log_count() -> int:
    """Count sync_log rows."""
    from ego_server.db import get_connection

    conn = get_connection()
    try:
        return conn.execute("SELECT COUNT(*) AS n FROM sync_log").fetchone()["n"]
    finally:
        conn.close()


def test_studio_save_unauthorized(studio_env: TestClient) -> None:
    r = studio_env.put("/admin/tasks/F1/studio", json=_save_payload())
    assert r.status_code == 401


def test_studio_save_forbidden_for_student(studio_env: TestClient) -> None:
    s_token, _ = _make_student(studio_env)
    r = studio_env.put(
        "/admin/tasks/F1/studio",
        json=_save_payload(),
        headers=_auth_headers(s_token),
    )
    assert r.status_code == 403


def test_studio_save_forbidden_for_mentor(studio_env: TestClient) -> None:
    m_token, _ = _create_user(studio_env, "mentor1", "pw", "mentor")
    r = studio_env.put(
        "/admin/tasks/F1/studio",
        json=_save_payload(),
        headers=_auth_headers(m_token),
    )
    assert r.status_code == 403


def test_studio_save_admin_happy_sync(studio_env: TestClient) -> None:
    """Admin save: all 3 files written, tasks row + task_versions + sync_log updated."""
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    etag = _get_studio_etag(studio_env, a_token)
    before = _read_canonical(studio_env)
    before_row = _db_task_row()
    before_versions = _db_task_versions()
    before_log_count = _db_sync_log_count()

    r = studio_env.put(
        "/admin/tasks/F1/studio",
        json=_save_payload(expected_content_etag=etag),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["task_id"] == "F1"
    assert data["new_version"] != "1.0.0"  # version was bumped
    assert data["sync"]["status"] == "success"
    assert data["sync"]["errors"] == 0
    assert data["sync"]["updated"] >= 1
    assert data["content_etag"]  # new etag returned for UI

    # --- all 3 canonical files were written with candidate content ---
    after = _read_canonical(studio_env)
    assert after["task_f1.md"] != before["task_f1.md"]
    assert "id: F1" in after["task_f1.md"]  # frontmatter present
    assert after["task_f1.solution.py"] == _VALID_SOLUTION
    assert after["task_f1.tests.py"] == _VALID_TESTS

    # --- tasks row updated ---
    row = _db_task_row()
    assert row is not None
    assert row["version"] == data["new_version"]
    assert row["content_hash"] != before_row["content_hash"]

    # --- task_versions row added ---
    versions = _db_task_versions()
    assert len(versions) > len(before_versions)
    assert any(v["version"] == data["new_version"] for v in versions)

    # --- sync_log row added ---
    assert _db_sync_log_count() == before_log_count + 1


def test_studio_save_stale_expected_version_unchanged(studio_env: TestClient) -> None:
    """Stale expected_version → 409, files and DB unchanged."""
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    before = _read_canonical(studio_env)
    before_row = _db_task_row()

    r = studio_env.put(
        "/admin/tasks/F1/studio",
        json=_save_payload(expected_version="0.9.0"),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 409
    assert "expected_version" in r.json()["detail"]

    # Files and DB must be byte-identical / unchanged.
    assert _read_canonical(studio_env) == before
    assert _db_task_row() == before_row


def test_studio_save_non_bumped_version_unchanged(studio_env: TestClient) -> None:
    """Content changed + version not bumped (declare) → 409, files/DB unchanged."""
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    etag = _get_studio_etag(studio_env, a_token)
    before = _read_canonical(studio_env)
    before_row = _db_task_row()

    r = studio_env.put(
        "/admin/tasks/F1/studio",
        json=_save_payload(
            expected_content_etag=etag,
            markdown=_valid_candidate_md(version="1.0.0", title="Changed"),
        ),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 409
    assert "declare" in r.json()["detail"]

    assert _read_canonical(studio_env) == before
    assert _db_task_row() == before_row


def test_studio_save_malformed_candidate_unchanged(studio_env: TestClient) -> None:
    """Malformed frontmatter → 422, canonical files unchanged."""
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    before = _read_canonical(studio_env)

    bad_md = "---\nid: F1\ntitle: Test\n\n# Задача F1: Test\n\n## Условие\nx\n"
    r = studio_env.put(
        "/admin/tasks/F1/studio",
        json=_save_payload(markdown=bad_md),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 422
    assert "frontmatter" in r.json()["detail"].lower()
    assert _read_canonical(studio_env) == before


def test_studio_save_traversal_blocked(studio_env: TestClient) -> None:
    """Traversal md_path → 409, files unchanged."""
    from ego_server.db import get_connection

    conn = get_connection()
    try:
        conn.execute("UPDATE tasks SET md_path = ? WHERE id = 'F1'", ("../secret.md",))
        conn.commit()
    finally:
        conn.close()

    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.put(
        "/admin/tasks/F1/studio",
        json=_save_payload(),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 409
    assert "escapes" in r.json()["detail"]


def test_studio_save_read_only_blocked(tmp_path, monkeypatch) -> None:
    """Unconfigured repo → 409, no files touched."""
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
        r = c.put(
            "/admin/tasks/F1/studio",
            json=_save_payload(),
            headers=_auth_headers(a_token),
        )
        assert r.status_code == 409
        assert "read-only" in r.json()["detail"].lower()


def test_studio_save_sync_failure_restores_files_and_db(studio_env: TestClient) -> None:
    """Simulated sync failure → 409, all files restored, DB unchanged."""
    from ego_server.sync import SyncResult

    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    etag = _get_studio_etag(studio_env, a_token)
    before = _read_canonical(studio_env)
    before_row = _db_task_row()
    before_versions = _db_task_versions()
    before_log_count = _db_sync_log_count()

    # Monkeypatch sync_from_path to return an error result.
    import ego_server.routers.admin as admin_mod

    def _failing_sync(conn, repo_path, *, source="manual", repo_url=""):
        return SyncResult(
            added=0,
            updated=0,
            skipped=0,
            errors=1,
            error_details=["simulated sync failure"],
            started_at="2026-01-01T00:00:00Z",
            finished_at="2026-01-01T00:00:01Z",
            log_id=999,
        )

    original_sync = admin_mod.sync_from_path
    admin_mod.sync_from_path = _failing_sync
    try:
        r = studio_env.put(
            "/admin/tasks/F1/studio",
            json=_save_payload(expected_content_etag=etag),
            headers=_auth_headers(a_token),
        )
    finally:
        admin_mod.sync_from_path = original_sync

    assert r.status_code == 409
    assert "sync" in r.json()["detail"].lower()
    # Honest messaging: claims "restored" only when restoration succeeded.
    assert "restored" in r.json()["detail"].lower()
    assert "all changes rolled back" not in r.json()["detail"].lower()

    # All canonical files must be restored to their original bytes.
    assert _read_canonical(studio_env) == before

    # DB must be unchanged: task row, task_versions, sync_log count.
    assert _db_task_row() == before_row
    assert _db_task_versions() == before_versions
    assert _db_sync_log_count() == before_log_count


# === Task Studio writability policy: validate/save 409 for non-declare ===


def test_studio_validate_auto_minor_409_no_write(studio_env: TestClient) -> None:
    """auto_minor project → validate 409, canonical bytes unchanged."""
    _set_project_policy("p1", "auto_minor")
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    before = _read_canonical(studio_env)
    r = studio_env.post(
        "/admin/tasks/F1/studio/validate",
        json=_validate_payload(),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 409
    assert "auto_minor" in r.json()["detail"]
    assert _read_canonical(studio_env) == before


def test_studio_validate_missing_project_409(studio_env: TestClient) -> None:
    """Missing project row → validate 409."""
    _set_task_project("F1", "ghost")
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.post(
        "/admin/tasks/F1/studio/validate",
        json=_validate_payload(),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 409
    assert "ghost" in r.json()["detail"]


def test_studio_validate_legacy_null_project_409(studio_env: TestClient) -> None:
    """Legacy NULL project_id → validate 409."""
    _set_task_project("F1", None)
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.post(
        "/admin/tasks/F1/studio/validate",
        json=_validate_payload(),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 409
    assert "legacy" in r.json()["detail"].lower()


def test_studio_save_auto_minor_409_no_write(studio_env: TestClient) -> None:
    """auto_minor project → save 409, canonical files + DB unchanged."""
    _set_project_policy("p1", "auto_minor")
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    before = _read_canonical(studio_env)
    before_row = _db_task_row()
    r = studio_env.put(
        "/admin/tasks/F1/studio",
        json=_save_payload(),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 409
    assert "auto_minor" in r.json()["detail"]
    assert _read_canonical(studio_env) == before
    assert _db_task_row() == before_row


def test_studio_save_legacy_null_project_409_no_write(studio_env: TestClient) -> None:
    """Legacy NULL project_id → save 409, canonical files + DB unchanged."""
    _set_task_project("F1", None)
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    before = _read_canonical(studio_env)
    before_row = _db_task_row()
    r = studio_env.put(
        "/admin/tasks/F1/studio",
        json=_save_payload(),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 409
    assert _read_canonical(studio_env) == before
    assert _db_task_row() == before_row


def test_studio_canonical_auto_minor_db_declare_read_only(
    studio_env: TestClient,
) -> None:
    """DB project stays 'declare' but canonical project.yaml is changed to
    auto_minor → GET is browse/read-only; validate and save return 409 with
    canonical bytes unchanged. Fixture isolation restores the file; nothing
    is restored manually here.

    Regression: the writability cross-check must consult the canonical
    content-repo discovery (``discover_repo``) project policy, not trust
    the DB ``projects.version_policy`` alone. A DB 'declare' row paired
    with a canonical 'auto_minor' project is a divergence and must be
    read-only with an actionable reason, while still serving canonical
    content for browse.
    """
    from ego_server.content_config import content_settings

    repo = content_settings.to_config().resolved_local_path
    project_yaml = repo / "projects" / "p1" / "project.yaml"
    project_yaml.write_text(
        "id: p1\nname: P1\nversion: '1.0.0'\nversion_policy: auto_minor\n",
        encoding="utf-8",
    )

    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    before = _read_canonical(studio_env)
    before_row = _db_task_row()

    # GET: browse/read-only — content returned, writable=False.
    r = studio_env.get("/admin/tasks/F1/studio", headers=_auth_headers(a_token))
    assert r.status_code == 200
    data = r.json()
    assert data["writable"] is False
    # version_policy reflects the DB row (for browse display), not canonical.
    assert data["version_policy"] == "declare"
    assert "auto_minor" in data["read_only_reason"]
    assert data["markdown"]
    assert data["solution_py"]
    assert data["tests_py"]

    # validate: 409, canonical bytes unchanged.
    r = studio_env.post(
        "/admin/tasks/F1/studio/validate",
        json=_validate_payload(),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 409
    assert "auto_minor" in r.json()["detail"]
    assert _read_canonical(studio_env) == before

    # save: 409, canonical bytes + DB unchanged.
    r = studio_env.put(
        "/admin/tasks/F1/studio",
        json=_save_payload(),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 409
    assert "auto_minor" in r.json()["detail"]
    assert _read_canonical(studio_env) == before
    assert _db_task_row() == before_row


# === Task Studio: tests_py mandatory + smoke @case ===


def test_studio_validate_empty_tests_rejected_422(studio_env: TestClient) -> None:
    """Empty tests_py → 422, canonical bytes unchanged (no silent sidecar keep)."""
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    before = _read_canonical(studio_env)
    r = studio_env.post(
        "/admin/tasks/F1/studio/validate",
        json=_validate_payload(tests_py=""),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 422
    assert "tests_py" in r.json()["detail"].lower()
    # Canonical files (including the existing tests sidecar) must be unchanged.
    assert _read_canonical(studio_env) == before


def test_studio_validate_whitespace_tests_rejected_422(studio_env: TestClient) -> None:
    """Whitespace-only tests_py → 422."""
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.post(
        "/admin/tasks/F1/studio/validate",
        json=_validate_payload(tests_py="   \n\t  \n"),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 422
    assert "tests_py" in r.json()["detail"].lower()


def test_studio_validate_full_only_tests_rejected_422(studio_env: TestClient) -> None:
    """Only @case(level='full') cases → 422 (no smoke case)."""
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    full_only = (
        "from solution import task_f1\n\n"
        '@case(args=(1,), expected=1, level="full")\n'
        "def t():\n    assert task_f1(1) == 1\n"
    )
    r = studio_env.post(
        "/admin/tasks/F1/studio/validate",
        json=_validate_payload(tests_py=full_only),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 422
    assert "smoke" in r.json()["detail"].lower()


def test_studio_validate_bare_case_smoke_ok(studio_env: TestClient) -> None:
    """Bare @case (no call) counts as smoke → validate 200."""
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    etag = _get_studio_etag(studio_env, a_token)
    bare = "from solution import task_f1\n\n@case\ndef t():\n    assert task_f1() == 42\n"
    r = studio_env.post(
        "/admin/tasks/F1/studio/validate",
        json=_validate_payload(expected_content_etag=etag, tests_py=bare),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 200, r.text


def test_studio_validate_called_case_no_level_smoke_ok(studio_env: TestClient) -> None:
    """@case(...) with absent level → default smoke → validate 200."""
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    etag = _get_studio_etag(studio_env, a_token)
    tests = (
        "from solution import task_f1\n\n"
        "@case(args=(1,), expected=1)\n"
        "def t():\n    assert task_f1(1) == 1\n"
    )
    r = studio_env.post(
        "/admin/tasks/F1/studio/validate",
        json=_validate_payload(expected_content_etag=etag, tests_py=tests),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 200, r.text


def test_studio_validate_called_case_smoke_level_ok(studio_env: TestClient) -> None:
    """@case(level='smoke') → smoke → validate 200."""
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    etag = _get_studio_etag(studio_env, a_token)
    tests = (
        "from solution import task_f1\n\n"
        '@case(args=(1,), expected=1, level="smoke")\n'
        "def t():\n    assert task_f1(1) == 1\n"
    )
    r = studio_env.post(
        "/admin/tasks/F1/studio/validate",
        json=_validate_payload(expected_content_etag=etag, tests_py=tests),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 200, r.text


def test_studio_validate_mixed_smoke_and_full_ok(studio_env: TestClient) -> None:
    """At least one smoke case among full cases → validate 200."""
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    etag = _get_studio_etag(studio_env, a_token)
    tests = (
        "from solution import task_f1\n\n"
        '@case(args=(1,), expected=1, level="full")\n'
        "@case(args=(2,), expected=2)\n"
        "def t(n):\n    return task_f1(n)\n"
    )
    r = studio_env.post(
        "/admin/tasks/F1/studio/validate",
        json=_validate_payload(expected_content_etag=etag, tests_py=tests),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 200, r.text


def test_studio_save_empty_tests_rejected_unchanged(studio_env: TestClient) -> None:
    """Empty tests_py on save → 422, canonical files (incl. tests sidecar) + DB unchanged."""
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    before = _read_canonical(studio_env)
    before_row = _db_task_row()
    r = studio_env.put(
        "/admin/tasks/F1/studio",
        json=_save_payload(tests_py=""),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 422
    assert "tests_py" in r.json()["detail"].lower()
    # The existing canonical tests sidecar must NOT be silently kept/wiped.
    assert _read_canonical(studio_env) == before
    assert _db_task_row() == before_row


def test_studio_save_full_only_tests_rejected_unchanged(studio_env: TestClient) -> None:
    """Only full cases on save → 422, canonical files + DB unchanged."""
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    before = _read_canonical(studio_env)
    before_row = _db_task_row()
    full_only = (
        "from solution import task_f1\n\n"
        '@case(args=(1,), expected=1, level="full")\n'
        "def t():\n    assert task_f1(1) == 1\n"
    )
    r = studio_env.put(
        "/admin/tasks/F1/studio",
        json=_save_payload(tests_py=full_only),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 422
    assert "smoke" in r.json()["detail"].lower()
    assert _read_canonical(studio_env) == before
    assert _db_task_row() == before_row


# === Task Studio: optimistic concurrency (content_etag) ===


def test_studio_validate_stale_content_etag_409(studio_env: TestClient) -> None:
    """A stale expected_content_etag (not matching fresh canonical) → 409."""
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    r = studio_env.post(
        "/admin/tasks/F1/studio/validate",
        json=_validate_payload(expected_content_etag="stale-etag-value"),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 409
    assert "expected_content_etag" in r.json()["detail"]


def test_studio_save_external_mutation_etag_mismatch_409(
    studio_env: TestClient,
) -> None:
    """External mutation of canonical files between GET and save → 409 etag mismatch.

    The save's pre-write etag re-check (inside BEGIN IMMEDIATE) must detect
    that the canonical bytes changed since the client's GET and reject with
    409, leaving zero writes.
    """
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    etag = _get_studio_etag(studio_env, a_token)
    before = _read_canonical(studio_env)
    before_row = _db_task_row()

    # Externally mutate the canonical markdown (simulating another editor).
    from ego_server.content_config import content_settings

    repo = content_settings.to_config().resolved_local_path
    md_path = repo / _STUDIO_FOLDER_REL / "task_f1.md"
    md_path.write_bytes(b"# Externally mutated\n")

    r = studio_env.put(
        "/admin/tasks/F1/studio",
        json=_save_payload(expected_content_etag=etag),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 409
    assert "expected_content_etag" in r.json()["detail"]

    # Zero writes: the externally mutated content must remain, not the candidate.
    after = _read_canonical(studio_env)
    assert after["task_f1.md"] == "# Externally mutated\n"
    assert after["task_f1.solution.py"] == before["task_f1.solution.py"]
    assert after["task_f1.tests.py"] == before["task_f1.tests.py"]
    # DB unchanged.
    assert _db_task_row() == before_row


def test_studio_save_parallel_one_wins_one_409(studio_env: TestClient) -> None:
    """Two saves with the same initial version+etag, distinct valid bumped
    candidates: exactly one succeeds (200) and one fails (409). The winner's
    canonical bytes and DB state are consistent.
    """
    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    etag = _get_studio_etag(studio_env, a_token)
    # Two distinct valid candidates with different bumped versions.
    cand_a_md = _valid_candidate_md(version="2.0.0", title="Alpha")
    cand_b_md = _valid_candidate_md(version="3.0.0", title="Beta")
    cand_a_sol = "def task_f1():\n    return 42  # alpha\n"
    cand_b_sol = "def task_f1():\n    return 42  # beta\n"

    r1 = studio_env.put(
        "/admin/tasks/F1/studio",
        json=_save_payload(
            expected_content_etag=etag,
            markdown=cand_a_md,
            solution_py=cand_a_sol,
        ),
        headers=_auth_headers(a_token),
    )
    r2 = studio_env.put(
        "/admin/tasks/F1/studio",
        json=_save_payload(
            expected_content_etag=etag,
            markdown=cand_b_md,
            solution_py=cand_b_sol,
        ),
        headers=_auth_headers(a_token),
    )

    statuses = sorted([r1.status_code, r2.status_code])
    assert statuses == [200, 409], f"expected [200, 409], got {statuses}"

    # Identify the winner (200) and loser (409).
    if r1.status_code == 200:
        winner, loser = r1, r2
        winner_md, winner_sol = cand_a_md, cand_a_sol
    else:
        winner, loser = r2, r1
        winner_md, winner_sol = cand_b_md, cand_b_sol

    # Loser: 409 with etag or version mismatch detail.
    assert (
        "expected_version" in loser.json()["detail"]
        or "expected_content_etag" in loser.json()["detail"]
    )

    # Winner: canonical bytes match the winner's candidate.
    after = _read_canonical(studio_env)
    assert after["task_f1.md"] == winner_md
    assert after["task_f1.solution.py"] == winner_sol
    assert after["task_f1.tests.py"] == _VALID_TESTS

    # Winner: DB version matches the winner's candidate version.
    row = _db_task_row()
    assert row is not None
    assert row["version"] == winner.json()["new_version"]

    # Winner: response returns a new content_etag.
    assert winner.json()["content_etag"]
    # The new etag must differ from the original (content changed).
    assert winner.json()["content_etag"] != etag


# === Task Studio: post-sync exactness (content_hash) ===


def test_studio_save_content_hash_matches_candidate(studio_env: TestClient) -> None:
    """After save, DB content_hash == candidate's parsed content_hash, and
    parsing the saved canonical file yields the same hash.
    """
    from ego.parser import parse_task_file
    from ego_server.content_config import content_settings

    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    etag = _get_studio_etag(studio_env, a_token)

    r = studio_env.put(
        "/admin/tasks/F1/studio",
        json=_save_payload(expected_content_etag=etag),
        headers=_auth_headers(a_token),
    )
    assert r.status_code == 200, r.text

    # DB content_hash must match the candidate's parsed content_hash.
    row = _db_task_row()
    assert row is not None
    # Parse the saved canonical file and verify its content_hash matches DB.
    repo = content_settings.to_config().resolved_local_path
    saved_md = repo / _STUDIO_FOLDER_REL / "task_f1.md"
    parsed_saved = parse_task_file(saved_md)
    assert row["content_hash"] == parsed_saved.content_hash


# === Task Studio: rollback failure honesty ===


def test_studio_save_second_replace_failure_restores_first_500(
    studio_env: TestClient,
) -> None:
    """Failure during the second os.replace → 500, first replaced file restored."""
    import ego_server.routers.admin as admin_mod

    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    etag = _get_studio_etag(studio_env, a_token)
    before = _read_canonical(studio_env)
    before_row = _db_task_row()

    original_replace = admin_mod._atomic_replace
    call_count = [0]

    def _failing_second_replace(path, content, backup):
        call_count[0] += 1
        if call_count[0] == 2:
            raise OSError("simulated second replace failure")
        return original_replace(path, content, backup)

    admin_mod._atomic_replace = _failing_second_replace
    try:
        r = studio_env.put(
            "/admin/tasks/F1/studio",
            json=_save_payload(expected_content_etag=etag),
            headers=_auth_headers(a_token),
        )
    finally:
        admin_mod._atomic_replace = original_replace

    assert r.status_code == 500
    detail = r.json()["detail"].lower()
    # Honest messaging: does not claim "all changes rolled back".
    assert "all changes rolled back" not in detail

    # The first replaced file (md) must be restored to its original bytes.
    after = _read_canonical(studio_env)
    assert after == before, "canonical files must be restored after second replace failure"
    # DB unchanged.
    assert _db_task_row() == before_row


def test_studio_save_second_replace_and_restore_failure_500(
    studio_env: TestClient,
) -> None:
    """Second replace fails AND restore fails → 500 saying rollback incomplete /
    manual recovery required; never says all changes rolled back.
    """
    import ego_server.routers.admin as admin_mod

    a_token, _ = _create_user(studio_env, "admin1", "pw", "admin")
    etag = _get_studio_etag(studio_env, a_token)

    original_replace = admin_mod._atomic_replace
    original_restore = admin_mod._restore_files
    call_count = [0]

    def _failing_second_replace(path, content, backup):
        call_count[0] += 1
        if call_count[0] == 2:
            raise OSError("simulated second replace failure")
        return original_replace(path, content, backup)

    def _failing_restore(backups):
        # Simulate restore failure: the first file (md) could not be restored.
        failed = [str(b.path) for b in backups if b.replaced]
        return admin_mod._RestoreResult(
            ok=False,
            failed_paths=failed,
            error="simulated restore failure",
        )

    admin_mod._atomic_replace = _failing_second_replace
    admin_mod._restore_files = _failing_restore
    try:
        r = studio_env.put(
            "/admin/tasks/F1/studio",
            json=_save_payload(expected_content_etag=etag),
            headers=_auth_headers(a_token),
        )
    finally:
        admin_mod._atomic_replace = original_replace
        admin_mod._restore_files = original_restore

    assert r.status_code == 500
    detail = r.json()["detail"].lower()
    # Must say rollback incomplete / manual recovery required.
    assert "rollback incomplete" in detail or "manual recovery" in detail
    # Must NOT claim all changes rolled back.
    assert "all changes rolled back" not in detail
