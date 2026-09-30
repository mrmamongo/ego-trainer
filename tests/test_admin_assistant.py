"""API contract tests for admin chat ownership, persistence, and provider failures."""

from __future__ import annotations

import base64
import importlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from tests.conftest import create_test_user


@pytest.fixture
def db_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "admin-assistant.sqlite3"
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
        base64.urlsafe_b64encode(b"A" * 32).decode("ascii"),
    )

    # The server settings are module singletons; reload them for each temp DB.
    for name in (
        "ego_server.config",
        "ego_server.content_config",
        "ego_server.auth",
        "ego_server.db",
        "ego_server.deps",
        "ego_server.service_settings",
        "ego_server.assistant",
        "ego_server.routers.auth",
        "ego_server.routers.check",
        "ego_server.routers.admin",
        "ego_server.routers.admin_settings",
        "ego_server.routers.admin_assistant",
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


def _enable_ai(client: TestClient, admin: str, db_path: Path) -> dict:
    snapshot_response = client.get("/admin/settings", headers=_headers(admin))
    assert snapshot_response.status_code == 200, snapshot_response.text
    snapshot = snapshot_response.json()
    config = {
        **snapshot["config"],
        "ai_enabled": True,
        "ai_base_url": "https://ai.test/v1",
        "ai_model": "test-model",
    }
    saved = client.put(
        "/admin/settings",
        headers=_headers(admin),
        json={
            "expected_revision": snapshot["revision"],
            "config": config,
            "api_key": "provider-test-key",
        },
    )
    assert saved.status_code == 200, saved.text
    return saved.json()


def _create_session(client: TestClient, token: str, title: str = "API test chat") -> dict:
    response = client.post(
        "/admin/assistant/sessions",
        headers=_headers(token),
        json={"title": title},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _mock_provider(
    monkeypatch: pytest.MonkeyPatch,
    handler,
) -> None:
    from ego_server import assistant

    monkeypatch.setattr(
        assistant,
        "_client",
        lambda timeout: httpx.AsyncClient(
            timeout=timeout,
            transport=httpx.MockTransport(handler),
            follow_redirects=False,
            trust_env=False,
        ),
    )


def _sse(*choices: dict) -> httpx.Response:
    payload = "".join(f"data: {json.dumps(choice)}\n\n" for choice in choices)
    payload += "data: [DONE]\n\n"
    return httpx.Response(
        200,
        headers={"content-type": "text/event-stream"},
        content=payload.encode("utf-8"),
    )


def test_assistant_requires_admin_authentication(client: TestClient, db_path: Path) -> None:
    assert client.get("/admin/assistant/sessions").status_code == 401
    assert (
        client.post("/admin/assistant/sessions", json={"title": "unauthenticated"}).status_code
        == 401
    )

    for role in ("student", "mentor"):
        token = _token(client, role)
        assert client.get("/admin/assistant/sessions", headers=_headers(token)).status_code == 403
        assert (
            client.post(
                "/admin/assistant/sessions",
                headers=_headers(token),
                json={"title": "forbidden"},
            ).status_code
            == 403
        )


def test_session_lists_and_reads_are_scoped_to_owning_admin(
    client: TestClient, db_path: Path
) -> None:
    admin_a = _token(client, "admin", "admin-a")
    admin_b = _token(client, "admin", "admin-b")
    own = _create_session(client, admin_a, "A's private chat")
    other = _create_session(client, admin_b, "B's private chat")

    listed_a = client.get("/admin/assistant/sessions", headers=_headers(admin_a))
    listed_b = client.get("/admin/assistant/sessions", headers=_headers(admin_b))
    assert [item["id"] for item in listed_a.json()] == [own["id"]]
    assert [item["id"] for item in listed_b.json()] == [other["id"]]

    hidden = client.get(f"/admin/assistant/sessions/{other['id']}", headers=_headers(admin_a))
    assert hidden.status_code == 404
    cannot_delete = client.delete(
        f"/admin/assistant/sessions/{other['id']}", headers=_headers(admin_a)
    )
    assert cannot_delete.status_code == 404


def test_chat_stream_is_saved_and_visible_in_later_session_read(
    client: TestClient,
    db_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    admin = _token(client, "admin")
    _enable_ai(client, admin, db_path)
    session = _create_session(client, admin)

    async def provider(_request: httpx.Request) -> httpx.Response:
        return _sse(
            {
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": "Проверка завершена."},
                        "finish_reason": "stop",
                    }
                ]
            }
        )

    _mock_provider(monkeypatch, provider)
    response = client.post(
        f"/admin/assistant/sessions/{session['id']}/messages",
        headers=_headers(admin),
        json={"content": "Покажи краткую сводку."},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert 'event: delta\ndata: {"text": "Проверка завершена."}' in response.text
    assert 'event: done\ndata: {"status": "complete"}' in response.text

    reread = client.get(f"/admin/assistant/sessions/{session['id']}", headers=_headers(admin))
    assert reread.status_code == 200
    messages = reread.json()["messages"]
    assert [(message["role"], message["content"], message["status"]) for message in messages] == [
        ("user", "Покажи краткую сводку.", "complete"),
        ("assistant", "Проверка завершена.", "complete"),
    ]


def test_disabled_assistant_rejects_message_without_persisting_it(
    client: TestClient, db_path: Path
) -> None:
    admin = _token(client, "admin")
    session = _create_session(client, admin)
    response = client.post(
        f"/admin/assistant/sessions/{session['id']}/messages",
        headers=_headers(admin),
        json={"content": "This should not be stored."},
    )
    assert response.status_code == 409

    reread = client.get(f"/admin/assistant/sessions/{session['id']}", headers=_headers(admin))
    assert reread.status_code == 200
    assert reread.json()["messages"] == []


@pytest.mark.parametrize(
    ("tool_name", "arguments"),
    [
        ("read_task", {"task_id": "TASK_SENTINEL"}),
        (
            "propose_settings",
            {"title": "Disable registration", "changes": {"registration_enabled": False}},
        ),
    ],
)
def test_disabled_tools_reject_provider_tool_calls_without_execution_or_context_leak(
    client: TestClient,
    db_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    tool_name: str,
    arguments: dict,
) -> None:
    admin = _token(client, "admin")
    snapshot_response = client.get("/admin/settings", headers=_headers(admin))
    assert snapshot_response.status_code == 200, snapshot_response.text
    snapshot = snapshot_response.json()
    config = {
        **snapshot["config"],
        "ai_enabled": True,
        "ai_tools_enabled": False,
        "ai_base_url": "https://ai.test/v1",
        "ai_model": "test-model",
    }
    saved = client.put(
        "/admin/settings",
        headers=_headers(admin),
        json={
            "expected_revision": snapshot["revision"],
            "config": config,
            "api_key": "provider-test-key",
        },
    )
    assert saved.status_code == 200, saved.text
    session = _create_session(client, admin)
    provider_requests: list[dict] = []

    async def provider(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        provider_requests.append(payload)
        function_arguments = json.dumps(arguments)
        return _sse(
            {
                "choices": [
                    {
                        "index": 0,
                        "delta": {
                            "tool_calls": [
                                {
                                    "index": 0,
                                    "id": "disabled-tool-call",
                                    "type": "function",
                                    "function": {
                                        "name": tool_name,
                                        "arguments": function_arguments,
                                    },
                                }
                            ]
                        },
                        "finish_reason": "tool_calls",
                    }
                ]
            }
        )

    _mock_provider(monkeypatch, provider)
    response = client.post(
        f"/admin/assistant/sessions/{session['id']}/messages",
        headers=_headers(admin),
        json={"content": "Give me a summary."},
    )
    assert response.status_code == 200
    assert "event: error" in response.text
    assert len(provider_requests) == 1
    assert "tools" not in provider_requests[0]
    assert "TASK_SENTINEL" not in json.dumps(provider_requests)

    history = client.get(f"/admin/assistant/sessions/{session['id']}", headers=_headers(admin))
    assert history.status_code == 200
    messages = history.json()["messages"]
    assert messages[-1]["role"] == "assistant"
    assert messages[-1]["status"] == "error"
    assert all(not message["proposals"] for message in messages)


def test_provider_unauthorized_error_is_sanitized_and_persisted_as_error(
    client: TestClient,
    db_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    admin = _token(client, "admin")
    _enable_ai(client, admin, db_path)
    session = _create_session(client, admin)

    async def provider(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": "secret provider response body"})

    _mock_provider(monkeypatch, provider)
    response = client.post(
        f"/admin/assistant/sessions/{session['id']}/messages",
        headers=_headers(admin),
        json={"content": "Проверь соединение."},
    )
    assert response.status_code == 200
    assert "event: error" in response.text
    assert "AI provider rejected access" in response.text
    assert "secret provider response body" not in response.text

    reread = client.get(f"/admin/assistant/sessions/{session['id']}", headers=_headers(admin))
    assert reread.status_code == 200
    messages = reread.json()["messages"]
    assert messages[-1]["role"] == "assistant"
    assert messages[-1]["status"] == "error"
    assert "AI provider rejected access" in messages[-1]["content"]
    assert "secret provider response body" not in messages[-1]["content"]


def test_active_reply_conflict_does_not_append_another_user_message(
    client: TestClient, db_path: Path
) -> None:
    admin = _token(client, "admin")
    _enable_ai(client, admin, db_path)
    session = _create_session(client, admin)
    stamp = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "INSERT INTO admin_chat_messages "
            "(id,session_id,role,content,status,created_at,updated_at) "
            "VALUES ('active-reply',?,?,?,'streaming',?,?)",
            (session["id"], "assistant", "", stamp, stamp),
        )

    response = client.post(
        f"/admin/assistant/sessions/{session['id']}/messages",
        headers=_headers(admin),
        json={"content": "A second request while one is active."},
    )
    assert response.status_code == 409
    reread = client.get(f"/admin/assistant/sessions/{session['id']}", headers=_headers(admin))
    assert [(message["role"], message["status"]) for message in reread.json()["messages"]] == [
        ("assistant", "streaming")
    ]


def test_deleting_session_cascades_messages_and_proposals(
    client: TestClient, db_path: Path
) -> None:
    admin = _token(client, "admin")
    session = _create_session(client, admin)
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "INSERT INTO admin_chat_messages "
            "(id,session_id,role,content,status,created_at,updated_at) "
            "VALUES ('assistant-message',?,'assistant','draft','complete',datetime('now'),datetime('now'))",
            (session["id"],),
        )
        connection.execute(
            "INSERT INTO admin_chat_proposals "
            "(id,message_id,kind,title,payload_json,created_at) "
            "VALUES ('proposal','assistant-message','settings','Draft','{}',datetime('now'))"
        )

    deleted = client.delete(f"/admin/assistant/sessions/{session['id']}", headers=_headers(admin))
    assert deleted.status_code == 204
    with sqlite3.connect(db_path) as connection:
        assert (
            connection.execute(
                "SELECT COUNT(*) FROM admin_chat_sessions WHERE id=?", (session["id"],)
            ).fetchone()[0]
            == 0
        )
        assert (
            connection.execute(
                "SELECT COUNT(*) FROM admin_chat_messages WHERE id='assistant-message'"
            ).fetchone()[0]
            == 0
        )
        assert (
            connection.execute(
                "SELECT COUNT(*) FROM admin_chat_proposals WHERE id='proposal'"
            ).fetchone()[0]
            == 0
        )


def test_ai_connection_check_reports_selected_model_and_latency(
    client: TestClient,
    db_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    admin = _token(client, "admin")
    _enable_ai(client, admin, db_path)
    observed: dict[str, object] = {}

    async def provider(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        observed.update(payload)
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "OK"}}]},
        )

    _mock_provider(monkeypatch, provider)
    response = client.post("/admin/settings/ai/test", headers=_headers(admin))
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["ok"] is True
    assert body["model"] == "test-model"
    assert isinstance(body["latency_ms"], int) and body["latency_ms"] >= 0
    assert body["answer"] == "OK"
    assert observed["model"] == "test-model"
    assert observed["stream"] is False


def test_settings_tool_streams_persisted_proposal_without_applying_it(
    client: TestClient,
    db_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    admin = _token(client, "admin")
    initial = _enable_ai(client, admin, db_path)
    session = _create_session(client, admin)
    proposal_args = json.dumps(
        {
            "title": "Отключить открытую регистрацию",
            "changes": {"registration_enabled": False},
        },
        ensure_ascii=False,
    )
    calls = 0

    async def provider(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return _sse(
                {
                    "choices": [
                        {
                            "index": 0,
                            "delta": {
                                "tool_calls": [
                                    {
                                        "index": 0,
                                        "id": "call-propose-settings",
                                        "type": "function",
                                        "function": {
                                            "name": "propose_settings",
                                            "arguments": proposal_args,
                                        },
                                    }
                                ]
                            },
                            "finish_reason": "tool_calls",
                        }
                    ]
                }
            )
        return _sse(
            {
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": "Подготовила предложение для проверки."},
                        "finish_reason": "stop",
                    }
                ]
            }
        )

    _mock_provider(monkeypatch, provider)
    response = client.post(
        f"/admin/assistant/sessions/{session['id']}/messages",
        headers=_headers(admin),
        json={"content": "Предложи отключить регистрацию."},
    )
    assert response.status_code == 200
    assert calls == 2
    assert "event: proposal" in response.text
    assert "Отключить открытую регистрацию" in response.text

    history = client.get(f"/admin/assistant/sessions/{session['id']}", headers=_headers(admin))
    assert history.status_code == 200
    assistant_message = history.json()["messages"][-1]
    assert assistant_message["role"] == "assistant"
    assert assistant_message["status"] == "complete"
    assert len(assistant_message["proposals"]) == 1
    proposal = assistant_message["proposals"][0]
    assert proposal["kind"] == "settings"
    assert proposal["title"] == "Отключить открытую регистрацию"
    assert proposal["payload"]["expected_revision"] == initial["revision"]
    assert proposal["payload"]["config"]["registration_enabled"] is False
    assert proposal["payload"]["changes"] == {"registration_enabled": False}

    current = client.get("/admin/settings", headers=_headers(admin)).json()
    assert current["revision"] == initial["revision"]
    assert current["config"]["registration_enabled"] is True


def test_oversized_api_key_validation_does_not_echo_secret(
    client: TestClient, db_path: Path
) -> None:
    admin = _token(client, "admin")
    settings_response = client.get("/admin/settings", headers=_headers(admin))
    assert settings_response.status_code == 200, settings_response.text
    snapshot = settings_response.json()
    marker = "oversize-secret-sentinel-"
    oversized_key = marker + ("x" * 20001)
    response = client.put(
        "/admin/settings",
        headers=_headers(admin),
        json={
            "expected_revision": snapshot["revision"],
            "config": snapshot["config"],
            "api_key": oversized_key,
        },
    )
    assert response.status_code == 422
    assert marker not in response.text
