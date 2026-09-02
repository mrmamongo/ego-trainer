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
            "INSERT INTO projects (id, name, description, version, \"order\", "
            "default_locale, tags, version_policy, created_at, updated_at) "
            "VALUES ('p1', 'P1', '', '1.0.0', 0, 'ru', '[]', 'declare', "
            "datetime('now'), datetime('now'))"
        )
        conn.execute(
            "INSERT INTO folders (id, project_id, code, name, description, "
            "\"order\", level, created_at, updated_at) "
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
