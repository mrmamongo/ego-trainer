"""Student cabinet shell, static assets and privacy-preserving page analytics."""

from __future__ import annotations

import importlib
import re

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def app_env(monkeypatch, tmp_path):
    monkeypatch.setenv("EGO_DB_PATH", str(tmp_path / "data" / "test.db"))
    monkeypatch.setenv("EGO_EXTENSION_DIR", str(tmp_path / "ext"))
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


def _daily_rows():
    from ego_server.db import get_connection

    conn = get_connection()
    try:
        return [dict(row) for row in conn.execute("SELECT * FROM analytics_daily")]
    finally:
        conn.close()


@pytest.mark.parametrize("url", ["/student", "/student/", "/student/tasks/V01", "/student/tasks/XL-A02"])
def test_student_entry_points_are_public_and_no_store(client, url):
    response = client.get(url)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert 'id="auth-screen"' in response.text
    assert 'id="dashboard"' in response.text
    assert 'src="/static/student.js"' in response.text


@pytest.mark.parametrize(
    "name", ["student.css", "student.js", "student-logic.js", "student-markdown.js"]
)
def test_student_assets_are_available(client, name):
    response = client.get(f"/static/{name}")
    assert response.status_code == 200
    assert response.content


def test_student_shell_is_self_contained_and_has_course_sidebar(client):
    html = client.get("/student").text
    assert 'href="/static/student.css"' in html
    assert html.index("student-logic.js") < html.index("student-markdown.js") < html.index("student.js")
    assert 'id="course-sidebar"' in html and 'id="sidebar-catalog"' in html
    assert "VS Code" in html
    assert "наставник" not in html.lower()
    assert not re.search(r'(?:src|href)="https?://', html)
    javascript = client.get("/static/student.js").text
    assert "ego_student_token" in javascript
    assert "/auth/forgejo/start" in javascript
    assert "vscode://ego-trainer.ego-trainer/open?task=" in javascript
    assert "solution_py" not in javascript
    markdown = client.get("/static/student-markdown.js").text
    assert "document.createElement('details')" in markdown
    assert "destination.startsWith('task:')" in markdown
    assert "destination.startsWith('lesson:')" in markdown


def test_student_cabinet_wires_soft_recommendations(client):
    """The cabinet reads GET /projects and the XL-A breakdown; old servers degrade."""
    javascript = client.get("/static/student.js").text
    assert "request('/projects')" in javascript
    assert "/progress/me/breakdown?project=" in javascript
    # Optional endpoints (404 on an old server) must not fail the whole page.
    assert "Promise.allSettled(" in javascript
    logic = client.get("/static/student-logic.js").text
    assert "readinessLine" in logic and "рекомендуем после" in logic
    assert "breakdownRows" in logic


def test_student_view_counter_covers_task_pages_and_ignores_bots(client):
    headers = {"User-Agent": "Mozilla/5.0"}
    assert client.get("/student", headers=headers).status_code == 200
    assert client.get("/student/tasks/V01", headers=headers).status_code == 200
    assert client.get("/student", headers={"User-Agent": "Friendly Crawl Bot"}).status_code == 200
    rows = _daily_rows()
    assert len(rows) == 1
    assert rows[0]["metric"] == "student_view"
    assert rows[0]["count"] == 2
