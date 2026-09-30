"""Regression tests for assistant task-edit freshness and total-turn timeout guards."""

from __future__ import annotations

import asyncio
import json
import time
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from tests.test_admin_assistant import (
    _create_session,
    _token,
    client as _client_fixture,  # noqa: F401 - shared isolated-client fixture
    db_path as _db_path_fixture,  # noqa: F401 - shared isolated-database fixture
)


client = _client_fixture

db_path = _db_path_fixture

TASK_ID = "B1"
TASK_TITLE = "A small editable task"


def _task_studio(version: str, etag: str) -> SimpleNamespace:
    return SimpleNamespace(
        version=version,
        content_etag=etag,
        writable=True,
        read_only_reason="",
        model_dump=lambda: {
            "task_id": TASK_ID,
            "version": version,
            "content_etag": etag,
            "markdown": "# Current task",
            "solution_py": "def solve():\n    return 1\n",
            "tests_py": "def test_solve():\n    assert solve() == 1\n",
        },
    )


def _call(name: str, arguments: dict) -> dict:
    return {
        "id": "call-test",
        "type": "function",
        "function": {"name": name, "arguments": json.dumps(arguments)},
    }


def _proposal_args() -> dict:
    return {
        "task_id": TASK_ID,
        "title": TASK_TITLE,
        "markdown": "# Proposed task",
        "solution_py": "def solve():\n    return 2\n",
        "tests_py": "def test_solve():\n    assert solve() == 2\n",
    }


def _chat_with_pending_reply(client: TestClient, db_path) -> tuple[str, str, str]:
    from ego_server.auth import decode_token
    from ego_server.assistant import begin_reply
    from ego_server.db import get_connection

    token = _token(client, "admin", "task-guard-admin")
    user_id = decode_token(token)["sub"]
    session = _create_session(client, token, "Freshness guard")
    db = get_connection()
    try:
        reply_id = begin_reply(db, session["id"], user_id, "Prepare a task edit")
    finally:
        db.close()
    return token, session["id"], reply_id


def _proposal_count(db, reply_id: str) -> int:
    return db.execute(
        "SELECT COUNT(*) FROM admin_chat_proposals WHERE message_id=?", (reply_id,)
    ).fetchone()[0]


def test_propose_task_edit_requires_a_prior_read_task(
    client: TestClient,
    db_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ego_server import assistant
    from ego_server.db import get_connection
    from ego_server.routers import admin as admin_router

    _, _, reply_id = _chat_with_pending_reply(client, db_path)
    fetched: list[str] = []

    async def get_task_studio(task_id: str, _db):
        fetched.append(task_id)
        return _task_studio("1.0.0", "etag-current")

    monkeypatch.setattr(admin_router, "get_task_studio", get_task_studio)
    db = get_connection()
    try:
        with pytest.raises(ValueError, match="Read the current task again"):
            asyncio.run(assistant._tool(db, _call("propose_task_edit", _proposal_args()), reply_id))
        assert fetched == [TASK_ID]
        assert _proposal_count(db, reply_id) == 0
    finally:
        db.close()


@pytest.mark.parametrize(
    ("changed_field", "changed_value"),
    [("version", "1.0.1"), ("content_etag", "etag-after-edit")],
)
def test_task_edit_proposal_is_rejected_if_task_changes_after_read(
    client: TestClient,
    db_path,
    monkeypatch: pytest.MonkeyPatch,
    changed_field: str,
    changed_value: str,
) -> None:
    from ego_server import assistant
    from ego_server.db import get_connection
    from ego_server.routers import admin as admin_router

    _, _, reply_id = _chat_with_pending_reply(client, db_path)
    calls = 0

    async def get_task_studio(_task_id: str, _db):
        nonlocal calls
        calls += 1
        version = "1.0.0"
        etag = "etag-before-edit"
        if calls > 1:
            if changed_field == "version":
                version = changed_value
            else:
                etag = changed_value
        return _task_studio(version, etag)

    monkeypatch.setattr(admin_router, "get_task_studio", get_task_studio)
    read_versions: dict[str, tuple[str, str]] = {}
    db = get_connection()
    try:
        read, proposal = asyncio.run(
            assistant._tool(
                db,
                _call("read_task", {"task_id": TASK_ID}),
                reply_id,
                read_versions,
            )
        )
        assert proposal is None
        assert read["version"] == "1.0.0"
        assert read_versions[TASK_ID] == ("1.0.0", "etag-before-edit")

        with pytest.raises(ValueError, match="Read the current task again"):
            asyncio.run(
                assistant._tool(
                    db,
                    _call("propose_task_edit", _proposal_args()),
                    reply_id,
                    read_versions,
                )
            )
        assert calls == 2
        assert _proposal_count(db, reply_id) == 0
    finally:
        db.close()


def test_whole_turn_deadline_persists_partial_reply_and_clears_streaming_state(
    client: TestClient,
    db_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ego_server import assistant
    from ego_server.db import get_connection
    from ego_server.service_settings import ConsoleSettings

    _, session_id, reply_id = _chat_with_pending_reply(client, db_path)
    # The timeout is intentionally tiny so this regression stays fast. model_copy
    # skips revalidation, allowing the test to exercise the real asyncio deadline.
    config = ConsoleSettings(
        ai_enabled=True,
        ai_base_url="https://ai.test/v1",
        ai_model="test-model",
    ).model_copy(update={"ai_timeout_seconds": 0.05})

    async def slow_provider(_config, _key: str, _history: list[dict]):
        yield {"delta": {"content": "partial reply"}}
        await asyncio.sleep(0.2)
        yield {"delta": {"content": "late reply"}}

    monkeypatch.setattr(assistant, "_provider", slow_provider)

    async def collect_events() -> list[str]:
        return [
            event
            async for event in assistant.stream_reply(session_id, reply_id, config, "test-key")
        ]

    started = time.monotonic()
    events = asyncio.run(asyncio.wait_for(collect_events(), timeout=1.0))
    assert time.monotonic() - started < 1.0
    assert any('"text": "partial reply"' in event for event in events)
    assert any("event: error" in event and "timed out" in event for event in events)

    db = get_connection()
    try:
        reply = db.execute(
            "SELECT content,status FROM admin_chat_messages WHERE id=?", (reply_id,)
        ).fetchone()
        assert reply["status"] == "error"
        assert "partial reply" in reply["content"]
        assert "timed out" in reply["content"]
        assert "late reply" not in reply["content"]
        assert (
            db.execute(
                "SELECT 1 FROM admin_chat_messages WHERE session_id=? AND status='streaming'",
                (session_id,),
            ).fetchone()
            is None
        )
    finally:
        db.close()
