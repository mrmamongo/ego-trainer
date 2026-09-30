"""An ASGI 2.4 browser disconnect cancels the provider and saves partial text."""

import asyncio

import pytest

import tests.test_admin_assistant as shared

client = shared.client
db_path = shared.db_path


@pytest.mark.parametrize("send_fails", [False, True])
def test_browser_disconnect_closes_provider_and_clears_pending_reply(
    client, db_path, monkeypatch, send_fails
):
    from ego_server import assistant
    from ego_server.auth import decode_token
    from ego_server.db import get_connection
    from ego_server.routers.admin_assistant import AssistantStreamingResponse
    from ego_server.service_settings import ConsoleSettings

    token = shared._token(client, "admin", "disconnect-admin")
    session = shared._create_session(client, token, "Disconnect test")
    db = get_connection()
    reply_id = assistant.begin_reply(db, session["id"], decode_token(token)["sub"], "hello")
    db.close()
    closed = []

    async def provider(*_args):
        try:
            yield {"delta": {"content": "partial reply"}}
            await asyncio.sleep(60)
        finally:
            closed.append(True)

    monkeypatch.setattr(assistant, "_provider", provider)

    async def run():
        delta_sent = asyncio.Event()

        async def send(message):
            if b"event: delta" in message.get("body", b""):
                if send_fails:
                    raise OSError("browser disconnected during the delta send")
                delta_sent.set()

        async def receive():
            await delta_sent.wait()
            return {"type": "http.disconnect"}

        config = ConsoleSettings(ai_enabled=True, ai_base_url="http://ai.test/v1", ai_model="mock")
        response = AssistantStreamingResponse(
            assistant.stream_reply(session["id"], reply_id, config, ""),
            reply_id=reply_id,
            media_type="text/event-stream",
        )
        await asyncio.wait_for(
            response({"type": "http", "asgi": {"spec_version": "2.4"}}, receive, send), 5
        )

        assert closed == [True], "Provider must close before event-loop teardown"

    asyncio.run(run())
    assert closed == [True]
    db = get_connection()
    try:
        reply = db.execute(
            "SELECT status,content FROM admin_chat_messages WHERE id=?", (reply_id,)
        ).fetchone()
        assert reply["status"] == "interrupted"
        assert reply["content"] == "partial reply"
    finally:
        db.close()
