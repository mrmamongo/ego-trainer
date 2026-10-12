"""The /ide in-browser workspace shell must serve and keep its assets available.

The IDE app itself is browser-persisted (IndexedDB per user); the server is a
stateless provider (auth + tasks + check), so these tests only pin the shell
and static assets contract.
"""

import pytest
from fastapi.testclient import TestClient

from ego_server.main import app


@pytest.mark.parametrize("url", ["/ide", "/ide/"])
def test_ide_entry_points_serve_workspace_shell(url):
    # Static shell needs no database; the APIs authenticate data access.
    response = TestClient(app).get(url)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert 'id="app"' in response.text
    assert 'src="/static/admin/ide.js"' in response.text


@pytest.mark.parametrize(
    "name",
    ["ide.html", "admin/ide.js"],
)
def test_ide_page_assets_are_available(name):
    response = TestClient(app).get(f"/static/{name}")
    assert response.status_code == 200
    assert response.content
