"""API contract tests for the persistent admin settings endpoints."""

from __future__ import annotations

import base64
import importlib
import sqlite3
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from tests.conftest import create_test_user


@pytest.fixture
def db_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Reload server modules against a per-test SQLite database and keys."""
    path = tmp_path / "admin-settings.sqlite3"
    for name in (
        "EGO_SERVICE_NAME",
        "EGO_REGISTRATION_ENABLED",
        "EGO_JWT_EXPIRE_MINUTES",
        "EGO_CHECK_TIMEOUT_SECONDS",
        "EGO_MAX_CODE_CHARS",
        "EGO_AI_ENABLED",
        "EGO_AI_BASE_URL",
        "EGO_AI_MODEL",
        "EGO_AI_API_KEY",
        "EGO_TASKS_REPO_URL",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("EGO_DB_PATH", str(path))
    monkeypatch.setenv("EGO_JWT_SECRET", "test-jwt-secret-that-is-long-enough-for-tests-123456")
    monkeypatch.setenv(
        "EGO_SETTINGS_ENCRYPTION_KEY",
        base64.urlsafe_b64encode(b"T" * 32).decode("ascii"),
    )

    # Keep each test isolated even though the application uses module-level settings.
    for name in (
        "ego_server.config",
        "ego_server.content_config",
        "ego_server.auth",
        "ego_server.db",
        "ego_server.deps",
        "ego_server.service_settings",
        "ego_server.routers.auth",
        "ego_server.routers.check",
        "ego_server.routers.admin",
        "ego_server.routers.admin_settings",
    ):
        module = importlib.import_module(name)
        importlib.reload(module)
    yield path
    monkeypatch.undo()
    for name in (
        "ego_server.config",
        "ego_server.content_config",
        "ego_server.auth",
        "ego_server.db",
    ):
        importlib.reload(importlib.import_module(name))


@pytest.fixture
def client(db_path: Path):
    import ego_server.main

    importlib.reload(ego_server.main)
    from ego_server.main import app

    with TestClient(app) as test_client:
        yield test_client


def _token(client: TestClient, role: str, username: str | None = None) -> str:
    return create_test_user(client, username or f"{role}-user", "test-password", role)[0]


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _settings(client: TestClient, token: str) -> dict:
    response = client.get("/admin/settings", headers=_headers(token))
    assert response.status_code == 200, response.text
    return response.json()


def _put_settings(
    client: TestClient,
    token: str,
    snapshot: dict,
    *,
    changes: dict | None = None,
    **extra: object,
):
    config = dict(snapshot["config"])
    config.update(changes or {})
    return client.put(
        "/admin/settings",
        headers=_headers(token),
        json={
            "expected_revision": snapshot["revision"],
            "config": config,
            **extra,
        },
    )


def test_settings_endpoints_require_authentication(client: TestClient) -> None:
    assert client.get("/admin/settings").status_code == 401
    assert client.get("/admin/settings/deployment").status_code == 401
    assert client.put("/admin/settings", json={}).status_code == 401


@pytest.mark.parametrize("role", ["student", "mentor"])
def test_settings_are_admin_only(client: TestClient, db_path: Path, role: str) -> None:
    token = _token(client, role)
    assert client.get("/admin/settings", headers=_headers(token)).status_code == 403
    assert client.get("/admin/settings/deployment", headers=_headers(token)).status_code == 403
    assert client.put("/admin/settings", headers=_headers(token), json={}).status_code == 403


def test_admin_settings_persist_and_advance_revision(client: TestClient, db_path: Path) -> None:
    admin = _token(client, "admin")
    before = _settings(client, admin)
    changes = {
        "service_name": "Training Console",
        "registration_enabled": False,
        "session_minutes": 45,
        "check_timeout_seconds": 11,
        "max_code_chars": 4000,
    }

    saved = _put_settings(client, admin, before, changes=changes)
    assert saved.status_code == 200, saved.text
    body = saved.json()
    assert body["revision"] == before["revision"] + 1
    assert {key: body["config"][key] for key in changes} == changes

    # A later request uses a fresh SQLite connection and must see the persisted row.
    reloaded = _settings(client, admin)
    assert reloaded["revision"] == body["revision"]
    assert {key: reloaded["config"][key] for key in changes} == changes


def test_stale_revision_is_rejected_without_overwriting_newer_settings(
    client: TestClient, db_path: Path
) -> None:
    admin = _token(client, "admin")
    initial = _settings(client, admin)
    first = _put_settings(client, admin, initial, changes={"service_name": "First update"})
    assert first.status_code == 200, first.text

    stale = client.put(
        "/admin/settings",
        headers=_headers(admin),
        json={
            "expected_revision": initial["revision"],
            "config": {**initial["config"], "service_name": "Stale update"},
        },
    )
    assert stale.status_code == 409
    current = _settings(client, admin)
    assert current["config"]["service_name"] == "First update"
    assert current["revision"] == first.json()["revision"]


def test_invalid_provider_url_is_rejected(client: TestClient, db_path: Path) -> None:
    admin = _token(client, "admin")
    current = _settings(client, admin)
    response = _put_settings(
        client,
        admin,
        current,
        changes={"ai_base_url": "https://user:password@example.invalid/v1"},
    )
    assert response.status_code in (400, 422)


def test_provider_key_is_encrypted_at_rest_and_never_returned(
    client: TestClient, db_path: Path
) -> None:
    admin = _token(client, "admin")
    current = _settings(client, admin)
    raw_key = "provider-secret-for-storage-test"
    response = _put_settings(client, admin, current, api_key=raw_key)
    assert response.status_code == 200, response.text
    assert response.json()["api_key_configured"] is True
    assert "api_key" not in response.json()
    assert raw_key not in response.text

    with sqlite3.connect(db_path) as connection:
        stored = connection.execute(
            "SELECT api_key_encrypted FROM service_settings WHERE id = 1"
        ).fetchone()[0]
    assert stored
    assert stored != raw_key
    assert raw_key not in stored

    reread = client.get("/admin/settings", headers=_headers(admin))
    assert reread.status_code == 200
    assert reread.json()["api_key_configured"] is True
    assert raw_key not in reread.text


@pytest.mark.parametrize(("mutation", "expected_status"), [("demote", 403), ("delete", 401)])
def test_demoted_or_revoked_admin_token_loses_settings_access(
    client: TestClient,
    db_path: Path,
    mutation: str,
    expected_status: int,
) -> None:
    from ego_server.auth import decode_token

    token = _token(client, "admin", username=f"admin-{mutation}")
    user_id = decode_token(token)["sub"]
    with sqlite3.connect(db_path) as connection:
        if mutation == "demote":
            connection.execute("UPDATE students SET role = 'student' WHERE id = ?", (user_id,))
        else:
            connection.execute("DELETE FROM students WHERE id = ?", (user_id,))

    response = client.get("/admin/settings", headers=_headers(token))
    assert response.status_code == expected_status


def test_disabled_registration_returns_forbidden(client: TestClient, db_path: Path) -> None:
    admin = _token(client, "admin")
    current = _settings(client, admin)
    saved = _put_settings(client, admin, current, changes={"registration_enabled": False})
    assert saved.status_code == 200, saved.text

    response = client.post(
        "/auth/register",
        json={"username": "registration-disabled", "password": "pw"},
    )
    assert response.status_code == 403


def test_session_minutes_controls_new_login_token_lifetime(
    client: TestClient, db_path: Path
) -> None:
    from ego_server.auth import decode_token

    admin = _token(client, "admin")
    current = _settings(client, admin)
    saved = _put_settings(client, admin, current, changes={"session_minutes": 37})
    assert saved.status_code == 200, saved.text

    create_test_user(client, "session-lifetime", "test-password", "student")
    login = client.post(
        "/auth/login",
        json={"username": "session-lifetime", "password": "test-password"},
    )
    assert login.status_code == 200, login.text
    claims = decode_token(login.json()["access_token"])
    assert claims["exp"] - claims["iat"] == 37 * 60


def test_check_rejects_code_over_persisted_character_limit(
    client: TestClient, db_path: Path
) -> None:
    admin = _token(client, "admin")
    current = _settings(client, admin)
    saved = _put_settings(client, admin, current, changes={"max_code_chars": 1000})
    assert saved.status_code == 200, saved.text

    student = _token(client, "student")
    response = client.post(
        "/check",
        headers=_headers(student),
        json={"task_id": "F1", "student_code": "x" * 1001},
    )
    assert response.status_code == 413


def test_check_uses_persisted_timeout(
    client: TestClient, db_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import ego_server.routers.check as check_router
    import ego_server.routers.tasks as tasks_router

    admin = _token(client, "admin")
    current = _settings(client, admin)
    saved = _put_settings(client, admin, current, changes={"check_timeout_seconds": 13})
    assert saved.status_code == 200, saved.text

    task_file = tmp_path / "task.md"
    task_file.write_text("placeholder", encoding="utf-8")
    observed: dict[str, float] = {}
    result = SimpleNamespace(
        task_id="F1",
        version="1.0.0",
        status="passed",
        passed_tests=1,
        total_tests=1,
        solution_hash="hash",
        results=[],
    )
    monkeypatch.setattr(
        check_router,
        "get_task_meta",
        lambda _db, _task_id: {"version": "1.0.0", "md_path": "task.md"},
    )
    monkeypatch.setattr(tasks_router, "_resolve_md_path", lambda _path: task_file)
    monkeypatch.setattr(check_router, "parse_task_file", lambda _path: object())

    def fake_run_check(_task, _code: str, *, timeout: float):
        observed["timeout"] = timeout
        return result

    monkeypatch.setattr(check_router, "run_check", fake_run_check)
    monkeypatch.setattr(check_router, "format_check_result", lambda _result: "ok")

    student = _token(client, "student")
    response = client.post(
        "/check",
        headers=_headers(student),
        json={"task_id": "F1", "student_code": "pass"},
    )
    assert response.status_code == 200, response.text
    assert observed["timeout"] == 13


def test_deployment_export_contains_no_provider_key(client: TestClient, db_path: Path) -> None:
    admin = _token(client, "admin")
    current = _settings(client, admin)
    saved = _put_settings(client, admin, current, api_key="deployment-secret")
    assert saved.status_code == 200, saved.text

    response = client.get("/admin/settings/deployment", headers=_headers(admin))
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "deployment-secret" not in response.text
    assert "<set-a-random-secret" in response.text
