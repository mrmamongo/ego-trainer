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
    # The site has a single mentor (the owner): no public mentor section or panel link.
    assert 'href="/panel"' not in response.text
    assert "наставник" not in response.text.lower()
    assert "{{BRAND_" not in response.text
    assert "195" in response.text and "56" in response.text
    assert "https://fonts" not in response.text


FOLDER_TITLES = [
    "Переменные",
    "Функции",
    "Циклы и роли переменных",
    "Числа и выражения",
    "range и while",
    "break, continue и вложенные циклы",
    "Строки",
    "Списки",
    "Функции глубже",
    "Мини-проекты",
]


def test_landing_keeps_collapsible_folders(client):
    import re

    html = client.get("/").text
    details = re.findall(r"<details\b[^>]*>.*?</details>", html, flags=re.S)
    assert len(details) == 10
    titles = [re.search(r'class="folder-name">([^<]+)<', block).group(1) for block in details]
    assert titles == FOLDER_TITLES
    for block in details:
        assert "<summary>" in block
    assert "https://fonts" not in html


def test_landing_has_no_external_resources(client):
    import re

    html = client.get("/").text
    tagged = re.findall(r"<(script|link|img|iframe|source)\b[^>]*>", html)
    for tag in tagged:
        for url in re.findall(r'(?:src|href)="([^"]+)"', tag):
            assert not re.match(r"(?i)\s*(https?:)?//", url), url
    assert "url(http" not in html
    assert "@import" not in html
    # Headers connect only to same-origin endpoints.
    for url in re.findall(r"(?:fetch|import)\('([^']+)'", html):
        assert url.startswith("/"), url


def test_landing_effects_respect_reduced_motion_and_no_js(client):
    html = client.get("/").text
    assert "@media(prefers-reduced-motion:reduce)" in html
    assert "@media(prefers-reduced-motion:no-preference)" in html
    # Content is hidden only after the inline script marks the document as JS-capable.
    assert "document.documentElement.classList.add('js')" in html
    assert ".js .reveal" in html
    head = html[: html.index("</head>")]
    assert "classList.add('js')" in head
    # No external libraries or trackers.
    assert "cdn." not in html and "google-analytics" not in html


def _inline_style_and_script(html: str) -> tuple[str, str]:
    import re

    style = re.search(r"(?s)<style>(.*?)</style>", html)
    scripts = re.findall(r"(?s)<script\b[^>]*>(.*?)</script>", html)
    assert style, "inline <style> is expected"
    return style.group(1), "\n".join(scripts)


def test_landing_folders_animate_without_js_dependency(client):
    import re

    html = client.get("/").text
    style, script = _inline_style_and_script(html)
    # Progressive enhancement: the <details> elements stay the source of truth.
    assert re.findall(r"<details\b", html) and "</summary>" in html
    assert "details.querySelector('[data-body]')" in script
    assert "body.animate(" in script  # Web Animations API for height + opacity
    # The icon rotates + -> x smoothly, and height/opacity share the timing.
    assert re.search(r"\.folder\[open\] \.folder-plus\{transform:rotate\(45deg\)", style)
    assert "transition:transform" in style


def test_landing_motion_respects_reduced_motion_and_hidden_tab(client):
    html = client.get("/").text
    style, script = _inline_style_and_script(html)
    # Everything animated sits behind the no-preference query; the reduce block kills the rest.
    assert style.count("@media(prefers-reduced-motion:no-preference)") == 1
    assert "transition:none!important;animation:none!important" in style
    # Infinite CSS loops (sticky notes) and JS loops (trace table) pause correctly.
    assert "'(prefers-reduced-motion: reduce)'" in script
    assert "visibilitychange" in script and "document.hidden" in script
    assert "IntersectionObserver" in script
    # The hero sequence waits are abortable and a cancelled run shows the final state.
    assert "new AbortController()" in script
    assert "function finish()" in script and "code.classList.add('done')" in script
    # No !important width override left to poison transitions in the hero.
    assert "measuring" not in script and "measuring" not in style


def test_landing_added_effects_stay_small(client):
    html = client.get("/").text
    style, script = _inline_style_and_script(html)
    # Everything added on top of the committed page: base CSS 16.6 KB + effects, base script
    # 0.5 KB + effects. Keeps the page lean (the brief asks for about 12 KB of additions).
    assert len(style.encode()) < 21_000, len(style.encode())
    assert len(script.encode()) < 12_000, len(script.encode())


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
