"""Student pages must survive direct navigation and browser refresh."""

import pytest
from fastapi.testclient import TestClient

from ego_server.main import app


@pytest.mark.parametrize(
    "url",
    [
        "/student",
        "/student/",
        "/student?q=F2&status=defense",
        "/student/tasks/F2",
        "/student/tasks/F2?tab=help",
        "/student/tasks/course%2Ftask%20one?tab=defense",
        "/student/tasks/unknown-task",
    ],
)
def test_student_entry_points_serve_authenticated_client_shell(url):
    # Static shells need no database or provider; the APIs authenticate data access.
    response = TestClient(app).get(url)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert 'id="auth-screen"' in response.text
    assert 'id="task-page"' in response.text
    assert 'src="/static/student.js"' in response.text


@pytest.mark.parametrize(
    "name",
    ["student.js", "student-navigation.js", "student-task-page.js", "student-tutor.js", "student.css"],
)
def test_student_page_assets_are_available(name):
    response = TestClient(app).get(f"/static/{name}")
    assert response.status_code == 200
    assert response.content
