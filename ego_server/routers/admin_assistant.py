"""Admin-scoped chat history and streaming replies."""

import uuid

import anyio
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ego_server import assistant
from ego_server.deps import DbDep
from ego_server.routers.admin_settings import Admin
from ego_server.service_settings import load_settings, provider_key

router = APIRouter()


class AssistantStreamingResponse(StreamingResponse):
    """Monitor disconnects even with ASGI 2.4 and close both provider generators."""

    def __init__(self, *args, reply_id: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.reply_id = reply_id

    async def __call__(self, scope, receive, send):
        try:
            async with anyio.create_task_group() as group:

                async def stream():
                    try:
                        await self.stream_response(send)
                    except OSError:
                        pass  # Client disconnected between chunks.
                    finally:
                        with anyio.CancelScope(shield=True):
                            await self.body_iterator.aclose()
                        group.cancel_scope.cancel()

                group.start_soon(stream)
                await self.listen_for_disconnect(receive)
                group.cancel_scope.cancel()
        finally:
            # Covers disconnects before the generator's first iteration.
            from ego_server.db import get_connection

            db = get_connection()
            try:
                db.execute(
                    "UPDATE admin_chat_messages SET status='interrupted',updated_at=? "
                    "WHERE id=? AND status='streaming'",
                    (assistant.now(), self.reply_id),
                )
                db.commit()
            finally:
                db.close()
        if self.background is not None:
            await self.background()


class NewSession(BaseModel):
    title: str = Field(default="Новый чат", min_length=1, max_length=120)


class ChatMessage(BaseModel):
    content: str = Field(min_length=1, max_length=8000)
    task_id: str | None = Field(default=None, max_length=200)


def _owned(db, session_id, user):
    value = assistant.session(db, session_id, user["sub"])
    if not value:
        raise HTTPException(404, "Chat not found")
    return value


@router.get("/assistant/sessions")
def list_sessions(db: DbDep, user: Admin) -> list[dict]:
    rows = db.execute(
        "SELECT * FROM admin_chat_sessions WHERE owner_id=? ORDER BY updated_at DESC LIMIT 100",
        (user["sub"],),
    ).fetchall()
    return [dict(row) for row in rows]


@router.post("/assistant/sessions", status_code=201)
def create_session(body: NewSession, db: DbDep, user: Admin) -> dict:
    session_id, stamp = uuid.uuid4().hex, assistant.now()
    db.execute(
        "INSERT INTO admin_chat_sessions (id,owner_id,title,created_at,updated_at) "
        "VALUES (?,?,?,?,?)",
        (session_id, user["sub"], body.title.strip(), stamp, stamp),
    )
    db.commit()
    return _owned(db, session_id, user)


@router.get("/assistant/sessions/{session_id}")
def read_session(session_id: str, db: DbDep, user: Admin) -> dict:
    value = _owned(db, session_id, user)
    return {"session": value, "messages": assistant.messages(db, session_id)}


@router.delete("/assistant/sessions/{session_id}", status_code=204)
def delete_session(session_id: str, db: DbDep, user: Admin) -> None:
    _owned(db, session_id, user)
    db.execute(
        "DELETE FROM admin_chat_sessions WHERE id=? AND owner_id=?", (session_id, user["sub"])
    )
    db.commit()


@router.post("/assistant/sessions/{session_id}/messages")
def send_message(session_id: str, body: ChatMessage, db: DbDep, user: Admin) -> StreamingResponse:
    _owned(db, session_id, user)
    config = load_settings(db)
    if not config.ai_enabled or not config.ai_base_url or not config.ai_model:
        raise HTTPException(409, "Configure and enable the AI assistant in Settings first")
    if not body.content.strip():
        raise HTTPException(422, "Message cannot be blank")
    try:
        key = provider_key(db)
        reply_id = assistant.begin_reply(db, session_id, user["sub"], body.content.strip())
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    return AssistantStreamingResponse(
        assistant.stream_reply(session_id, reply_id, config, key, body.task_id),
        reply_id=reply_id,
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/settings/ai/test")
async def test_ai_connection(db: DbDep, user: Admin) -> dict:
    try:
        return await assistant.test_connection(load_settings(db), provider_key(db))
    except (ValueError, httpx.HTTPError) as exc:
        message = str(exc) if isinstance(exc, ValueError) else "Cannot connect to AI provider"
        raise HTTPException(400, message) from exc


@router.get("/settings/ai/models")
async def ai_models(db: DbDep, user: Admin) -> list[str]:
    try:
        return await assistant.list_models(load_settings(db), provider_key(db))
    except (ValueError, httpx.HTTPError) as exc:
        message = str(exc) if isinstance(exc, ValueError) else "Cannot connect to AI provider"
        raise HTTPException(400, message) from exc
