"""The /panel and /ide shells must reference only static assets that exist.

The admin bundle, the theme and the IDE are produced by ``admin-ui/build.mjs``
into ``ego_server/static/admin/``. A shell that points at a missing file (or an
image that forgot to ship one) renders a broken page, so these tests parse the
served HTML and assert every ``/static`` reference resolves -- through the
server itself and on disk. They run against the built assets; when they are
absent they skip with the exact command that builds them.
"""

from __future__ import annotations

import importlib
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ego_server import static_pages

STATIC_DIR = static_pages.STATIC_DIR
_STATIC_REFERENCE = re.compile(r"""(?:src|href)\s*=\s*["'](/static/[^"'?#\s]+)""", re.IGNORECASE)


def static_references(html: str) -> list[str]:
    """Every ``/static/...`` path referenced by the HTML (query string dropped)."""
    return sorted(set(_STATIC_REFERENCE.findall(html)))


def static_file(url: str) -> Path:
    """Map a ``/static/<path>`` URL onto ``ego_server/static/<path>``."""
    assert url.startswith("/static/"), url
    return STATIC_DIR / url.removeprefix("/static/")


BUILT_ASSETS = (
    "admin/bundle.js",
    "admin/bundle.css",
    "admin/theme.css",
    "admin/ide.js",
    "admin/ide.css",
    "admin/workers/editor.worker.js",
    "admin/monaco.LICENSE.txt",
    "admin/shadcn.LICENSE.txt",
)


def _missing_built_assets() -> list[str]:
    return [name for name in BUILT_ASSETS if not (STATIC_DIR / name).is_file()]


pytestmark = pytest.mark.skipif(
    bool(_missing_built_assets()),
    reason="admin-ui is not built; run `cd admin-ui && npm ci && npm run build` "
    "(missing: " + ", ".join(_missing_built_assets()) + ")",
)


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("EGO_DB_PATH", str(tmp_path / "data" / "test.db"))
    monkeypatch.setenv("EGO_EXTENSION_DIR", str(tmp_path / "ext"))
    import ego_server.config

    importlib.reload(ego_server.config)
    import ego_server.db

    importlib.reload(ego_server.db)
    import ego_server.main

    importlib.reload(ego_server.main)
    static_pages.reset_asset_version()
    from ego_server.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.parametrize("url", ["/panel", "/panel/"])
def test_admin_page_references_only_existing_static_assets(client, url):
    response = client.get(url)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    references = static_references(response.text)
    assert references, "the admin shell references no static assets"
    for reference in references:
        assert static_file(reference).is_file(), (
            f"admin.html references {reference}, which is not in {STATIC_DIR}"
        )
        assert client.get(reference).status_code == 200, reference


@pytest.mark.parametrize("url", ["/ide", "/ide/", "/ide/task/V01", "/ide/room/abcdefghijklmnop"])
def test_ide_page_references_only_existing_static_assets(client, url):
    response = client.get(url)
    assert response.status_code == 200
    references = static_references(response.text)
    for reference in references:
        assert static_file(reference).is_file(), (
            f"ide.html references {reference}, which is not in {STATIC_DIR}"
        )
        assert client.get(reference).status_code == 200, reference


def test_admin_page_links_the_theme(client):
    html = client.get("/panel").text
    shell = (STATIC_DIR / "admin.html").read_text(encoding="utf-8")
    assert re.search(r'<link rel="stylesheet" href="/static/admin/theme\.css\?v=', html)
    assert 'href="/static/admin/bundle.css?v=' in html
    # The theme must load before the bundle's component CSS.
    assert html.index("theme.css") < html.index("bundle.css")
    assert '<meta name="theme-color" content="#09090b">' in html
    assert "var(--background, #09090b)" in html
    assert "{{STATIC_ASSET_VERSION}}" in shell  # filled at serve time
    assert "{{" not in html


def test_ide_page_links_theme_and_ide_styles(client):
    html = client.get("/ide").text
    assert 'href="/static/admin/theme.css?v=' in html
    assert 'href="/static/admin/ide.css?v=' in html
    assert 'src="/static/admin/ide.js?v=' in html


def test_html_asset_urls_are_content_versioned(client):
    versions = static_pages.asset_version_map()
    for url in ("/panel", "/ide"):
        html = client.get(url).text
        for asset in (
            "admin/theme.css",
            "admin/bundle.css",
            "admin/bundle.js",
            "admin/ide.css",
            "admin/ide.js",
        ):
            asset_url = f"/static/{asset}"
            if asset_url not in html:
                continue
            digest = versions[asset_url]
            assert f'"{asset_url}?v={digest}"' in html, (url, asset_url)


def test_asset_version_is_stable_across_reloads(client):
    first = static_pages.current_asset_version()
    static_pages.reset_asset_version()
    assert static_pages.current_asset_version() == first
    assert re.fullmatch(r"[0-9a-f]{12}", first)
    assert static_pages.current_asset_version() in client.get("/panel").text


def test_asset_version_ignores_unreferenced_files(monkeypatch, tmp_path):
    # Only referenced assets contribute; a stray file must not churn the version.
    monkeypatch.setattr(static_pages, "STATIC_DIR", tmp_path)
    (tmp_path / "admin").mkdir()
    (tmp_path / "admin" / "bundle.js").write_text("a", encoding="utf-8")
    static_pages.reset_asset_version()
    before = static_pages.current_asset_version()
    (tmp_path / "admin" / "unrelated.tmp").write_text("noise", encoding="utf-8")
    static_pages.reset_asset_version()
    assert static_pages.current_asset_version() == before
    (tmp_path / "admin" / "bundle.js").write_text("b", encoding="utf-8")
    static_pages.reset_asset_version()
    assert static_pages.current_asset_version() != before


def test_every_referenced_shell_asset_is_in_the_built_set(client):
    # Keep BUILT_ASSETS honest: anything a shell references must be in it, so
    # packaging/build checks cover the whole set.
    referenced = set()
    for url in ("/panel", "/ide"):
        referenced.update(static_references(client.get(url).text))
    built = {f"/static/{name}" for name in BUILT_ASSETS}
    admin_refs = {url for url in referenced if url.startswith("/static/admin/")}
    assert {url for url in admin_refs if not url.endswith((".png", ".svg", ".ico"))} <= built
