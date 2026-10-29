"""``scripts/check_static_assets.py`` must fail loudly on a broken asset.

The script is a release/CI gate, so these tests run it end to end against a
local server and against a temporary copy of ``ego_server/static`` with one
referenced file removed.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import threading
from pathlib import Path

import pytest
import uvicorn

from ego_server import static_pages

ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "scripts" / "check_static_assets.py"


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=180,
        cwd=ROOT,
    )


@pytest.mark.skipif(
    not (static_pages.STATIC_DIR / "admin" / "bundle.js").is_file(),
    reason="admin-ui is not built; run `cd admin-ui && npm ci && npm run build`",
)
def test_script_passes_for_a_local_static_tree():
    result = _run(["--local-dir", str(static_pages.STATIC_DIR)])
    assert result.returncode == 0, result.stdout + result.stderr
    assert "all referenced static assets are served" in result.stdout


def test_script_fails_when_a_referenced_asset_is_missing(tmp_path):
    copy = tmp_path / "static"
    shutil.copytree(static_pages.STATIC_DIR, copy)
    (copy / "admin").mkdir(exist_ok=True)
    (copy / "admin" / "theme.css").write_text(":root{}", encoding="utf-8")
    if (copy / "admin" / "bundle.js").is_file():
        (copy / "admin" / "bundle.js").unlink()
    result = _run(["--local-dir", str(copy)])
    assert result.returncode == 1
    assert "/static/admin/bundle.js" in result.stdout
    assert "HTTP 404" in result.stdout
    assert "failure(s)" in result.stdout


def test_script_requires_exactly_one_target():
    result = _run([])
    assert result.returncode == 2
    assert "exactly one of" in result.stderr


@pytest.fixture
def live_server(monkeypatch, tmp_path):
    monkeypatch.setenv("EGO_DB_PATH", str(tmp_path / "data" / "test.db"))
    monkeypatch.setenv("EGO_EXTENSION_DIR", str(tmp_path / "ext"))
    import importlib

    import ego_server.config

    importlib.reload(ego_server.config)
    import ego_server.db

    importlib.reload(ego_server.db)
    import ego_server.main

    importlib.reload(ego_server.main)
    from ego_server.main import app

    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=0, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    try:
        for _ in range(300):
            if server.started:
                break
            threading.Event().wait(0.05)
        assert server.started, "uvicorn did not start"
        port = server.servers[0].sockets[0].getsockname()[1]
        yield f"http://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        thread.join(timeout=20)


@pytest.mark.skipif(
    not (static_pages.STATIC_DIR / "admin" / "bundle.js").is_file(),
    reason="admin-ui is not built; run `cd admin-ui && npm ci && npm run build`",
)
def test_script_passes_against_a_running_server(live_server):
    result = _run([live_server])
    assert result.returncode == 0, result.stdout + result.stderr
    for page in ("/", "/panel", "/ide", "/student"):
        assert f"ok   {page}" in result.stdout
