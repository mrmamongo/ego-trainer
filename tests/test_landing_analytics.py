"""Public landing, brand rendering and privacy-preserving analytics."""

from __future__ import annotations

import importlib
import json
import sqlite3
import zipfile

import pytest
from fastapi.testclient import TestClient


def create_test_user(client, username: str, password: str, role: str) -> tuple[str, str]:
    from ego_server.auth import generate_user_id, hash_password
    from ego_server.db import get_connection

    conn = get_connection()
    try:
        user_id = generate_user_id()
        conn.execute(
            "INSERT INTO students (id, username, role, password_hash, created_at) "
            "VALUES (?, ?, ?, ?, datetime('now'))",
            (user_id, username, role, hash_password(password)),
        )
        conn.commit()
    finally:
        conn.close()
    response = client.post("/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"], user_id


@pytest.fixture
def app_env(monkeypatch, tmp_path):
    db_path = tmp_path / "data" / "test.db"
    ext_dir = tmp_path / "ext"
    ext_dir.mkdir()
    monkeypatch.setenv("EGO_DB_PATH", str(db_path))
    monkeypatch.setenv("EGO_EXTENSION_DIR", str(ext_dir))
    import ego_server.config

    importlib.reload(ego_server.config)
    import ego_server.db

    importlib.reload(ego_server.db)
    import ego_server.main

    importlib.reload(ego_server.main)
    return tmp_path


@pytest.fixture
def client(app_env):
    from ego_server.main import app

    with TestClient(app) as test_client:
        yield test_client


def _publish(client, app_env, version="0.2.0"):
    from ego_server.cli import main as cli_main

    vsix = app_env / "incoming" / f"cogito-{version}.vsix"
    vsix.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(vsix, "w") as archive:
        archive.writestr(
            "extension/package.json",
            json.dumps({"name": "ego-trainer", "version": version}),
        )
        archive.writestr("extension.vsixmanifest", "<PackageManifest/>")
    assert cli_main(["admin", "publish-extension", "--vsix", str(vsix)]) == 0


def _daily_rows():
    from ego_server.db import get_connection

    conn = get_connection()
    try:
        return [dict(row) for row in conn.execute("SELECT * FROM analytics_daily")]
    finally:
        conn.close()


def test_landing_is_public_complete_and_no_store(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert "Твой первый код" in response.text
    assert 'href="/extension/download"' in response.text
    assert 'href="/student"' in response.text
    assert 'href="/panel"' in response.text
    assert "{{BRAND_" not in response.text
    assert "195" in response.text and "56" in response.text
    assert "https://fonts" not in response.text


def test_landing_counter_upserts_and_ignores_bots(client):
    for _ in range(2):
        assert client.get("/", headers={"User-Agent": "Mozilla/5.0"}).status_code == 200
    assert client.get("/", headers={"User-Agent": "Friendly Crawl Bot"}).status_code == 200
    assert client.get("/student", headers={"User-Agent": "curl/8.0"}).status_code == 200
    rows = _daily_rows()
    assert len(rows) == 1
    assert rows[0]["metric"] == "landing_view"
    assert rows[0]["count"] == 2


def test_extension_counters_use_versions_and_ignore_landing_version_fetch(client, app_env):
    _publish(client, app_env)
    assert client.get("/extension/latest").status_code == 200
    assert _daily_rows() == []

    assert client.get(
        "/extension/latest", headers={"X-Cogito-Extension-Version": "0.1.9"}
    ).status_code == 200
    assert client.get("/extension/download").status_code == 200
    assert client.get(
        "/extension/download", headers={"User-Agent": "curl/8.0"}
    ).status_code == 200
    rows = _daily_rows()
    by_metric = {(row["metric"], row["key"]): row["count"] for row in rows}
    assert by_metric == {("extension_active", "0.1.9"): 1, ("extension_download", "0.2.0"): 1}


def test_analytics_requires_mentor_and_returns_learning_activity(client):
    student_token, student_id = create_test_user(client, "student", "pw", "student")
    assert client.get("/admin/analytics").status_code == 401
    assert client.get(
        "/admin/analytics", headers={"Authorization": f"Bearer {student_token}"}
    ).status_code == 403
    mentor_token, _ = create_test_user(client, "mentor", "pw", "mentor")

    client.get("/", headers={"User-Agent": "Mozilla/5.0"})
    from ego_server.db import get_connection

    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO runs
               (id, student_id, task_id, version, solution_hash, status, log, created_at)
               VALUES ('run-1', ?, 'F1', '1.0.0', 'hash', 'passed', '', datetime('now'))""",
            (student_id,),
        )
        conn.execute(
            """INSERT INTO progress
               (student_id, task_id, version, status, attempts, passed_tests,
                total_tests, last_run_at)
               VALUES (?, 'F1', '1.0.0', 'passed', 1, 2, 2, datetime('now'))""",
            (student_id,),
        )
        conn.commit()
    finally:
        conn.close()

    response = client.get(
        "/admin/analytics?days=30", headers={"Authorization": f"Bearer {mentor_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["totals"]["landing_views"] == 1
    assert data["learning"]["active_students_today"] == 1
    assert data["learning"]["active_students_week"] == 1
    assert data["learning"]["tasks_passed"] == 1
    assert data["learning"]["new_students"] == 1


def test_analytics_days_bounds(client):
    token, _ = create_test_user(client, "mentor", "pw", "mentor")
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/admin/analytics?days=0", headers=headers).status_code == 422
    assert client.get("/admin/analytics?days=366", headers=headers).status_code == 422


def test_analytics_migration_is_additive(tmp_path):
    from ego_server.db import init_schema

    path = tmp_path / "old.db"
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("CREATE TABLE students (id TEXT PRIMARY KEY)")
        conn.execute("INSERT INTO students VALUES ('keep-me')")
        init_schema(conn)
        assert conn.execute("SELECT id FROM students").fetchone()["id"] == "keep-me"
        conn.execute(
            "CREATE TABLE analytics_legacy_probe AS SELECT * FROM analytics_daily LIMIT 0"
        )
        assert conn.execute(
            "SELECT name FROM sqlite_master WHERE name = 'analytics_daily'"
        ).fetchone()
    finally:
        conn.close()
