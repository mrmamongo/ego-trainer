"""The dashboard shell must load the global theme before component styles."""

from fastapi.testclient import TestClient

from ego_server.main import app


def test_admin_shell_loads_theme_and_is_not_cached():
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    theme = response.text.index('href="/static/admin/theme.css"')
    components = response.text.index('href="/static/admin/bundle.css"')
    assert theme < components
    assert "background: var(--background" in response.text
