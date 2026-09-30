"""Browser authorization with a cookie-bound state and client PKCE handoff.

Clients poll using their own verifier. The callback exposes no provider/local
tokens and does not redirect to client-supplied URLs. SQLite allows multiple
workers and restart-safe, atomic consumption of short-lived flows.
"""

from __future__ import annotations

import secrets
import time
from typing import Literal
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel, Field, model_validator

from ego_server import config, forgejo
from ego_server.auth import create_token
from ego_server.deps import DbDep
from ego_server.models import TokenResponse
from ego_server.service_settings import load_settings

router = APIRouter()
_HEADERS = {"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"}


class StartRequest(BaseModel):
    code_challenge: str = Field(pattern=r"^[A-Za-z0-9_-]{43}$")
    client: Literal["browser", "vscode"] = "browser"
    callback_port: int | None = Field(default=None, ge=1024, le=65535)

    @model_validator(mode="after")
    def validate_callback(self):
        if (self.client == "vscode") != (self.callback_port is not None):
            raise ValueError("Only VSCode login requires a loopback callback port")
        return self


class ExchangeRequest(BaseModel):
    state: str = Field(pattern=r"^[A-Za-z0-9_-]{43}$")
    code_verifier: str = Field(pattern=r"^[A-Za-z0-9._~-]{43,128}$", repr=False)
    ticket: str = Field(default="", pattern=r"^([A-Za-z0-9_-]{43})?$", repr=False)


def _cookie(state: str) -> str:
    return "ego_oauth_" + state[:16]


def _flow(db, state: str):
    issuer, _, redirect_uri = forgejo.provider_config()
    row = db.execute(
        "SELECT * FROM oauth_flows WHERE state_hash=? AND expires_at>?",
        (forgejo.digest(state), int(time.time())),
    ).fetchone()
    if (
        row is None
        or row["issuer"] != issuer
        or row["client_id"] != config.settings.forgejo_client_id
        or row["redirect_uri"] != redirect_uri
    ):
        raise HTTPException(status_code=400, detail="Login attempt expired or invalid; start again")
    return row


@router.get("/providers")
async def providers() -> dict:
    enabled = False
    try:
        forgejo.provider_config()
        enabled = True
    except HTTPException:
        pass
    return {"forgejo": enabled, "local": config.settings.local_auth_enabled}


@router.post("/forgejo/start")
async def start(body: StartRequest, db: DbDep) -> JSONResponse:
    issuer, public_url, redirect_uri = forgejo.provider_config()
    state = secrets.token_urlsafe(32)
    verifier = secrets.token_urlsafe(48)
    now = int(time.time())
    db.execute("DELETE FROM oauth_flows WHERE expires_at<=?", (now,))
    db.execute(
        "INSERT INTO oauth_flows "
        "(state_hash,issuer,client_id,redirect_uri,verifier,challenge,expires_at,callback_port) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (
            forgejo.digest(state),
            issuer,
            config.settings.forgejo_client_id,
            redirect_uri,
            verifier,
            body.code_challenge,
            now + forgejo.FLOW_SECONDS,
            body.callback_port,
        ),
    )
    db.commit()
    return JSONResponse(
        {
            "state": state,
            "authorization_url": public_url + "/auth/forgejo/authorize?state=" + state,
            "expires_in": forgejo.FLOW_SECONDS,
        },
        headers=_HEADERS,
    )


@router.get("/forgejo/authorize")
async def authorize(db: DbDep, state: str = Query(pattern=r"^[A-Za-z0-9_-]{43}$")):
    row = _flow(db, state)
    binding = secrets.token_urlsafe(32)
    changed = db.execute(
        "UPDATE oauth_flows SET browser_hash=?,phase='browser' "
        "WHERE state_hash=? AND phase='pending'",
        (forgejo.digest(binding), row["state_hash"]),
    ).rowcount
    db.commit()
    if changed != 1:
        raise HTTPException(status_code=400, detail="Login attempt already opened; start again")
    response = RedirectResponse(
        row["issuer"]
        + "/login/oauth/authorize?"
        + urlencode(
            {
                "client_id": row["client_id"],
                "redirect_uri": row["redirect_uri"],
                "response_type": "code",
                "scope": "openid profile",
                "state": state,
                "code_challenge": forgejo.challenge(row["verifier"]),
                "code_challenge_method": "S256",
            }
        ),
        status_code=302,
        headers=_HEADERS,
    )
    response.set_cookie(
        _cookie(state),
        binding,
        max_age=forgejo.FLOW_SECONDS,
        httponly=True,
        secure=row["redirect_uri"].startswith("https://"),
        samesite="lax",
        path="/auth/forgejo/callback",
    )
    return response


@router.get("/forgejo/callback")
async def callback(
    request: Request,
    db: DbDep,
    state: str = Query(pattern=r"^[A-Za-z0-9_-]{43}$"),
    code: str = Query(default="", max_length=2048),
    error: str = Query(default="", max_length=255),
):
    row = _flow(db, state)
    binding = request.cookies.get(_cookie(state), "")
    if (
        not binding
        or len(binding) > 128
        or not binding.isascii()
        or not row["browser_hash"]
        or not secrets.compare_digest(forgejo.digest(binding), row["browser_hash"])
    ):
        raise HTTPException(status_code=400, detail="Login browser does not match; start again")
    changed = db.execute(
        "UPDATE oauth_flows SET phase='exchanging' WHERE state_hash=? AND phase='browser'",
        (row["state_hash"],),
    ).rowcount
    db.commit()
    if changed != 1:
        raise HTTPException(status_code=400, detail="Login callback already used")
    success = False
    ticket = secrets.token_urlsafe(32)
    try:
        if error or not code:
            raise ValueError("Authorization cancelled")
        subject, name = await forgejo.fetch_identity(code, row)
        db.execute("BEGIN IMMEDIATE")
        user_id = forgejo.resolve_user(db, row["issuer"], subject, name)
        db.execute(
            "UPDATE oauth_flows SET phase='ready',user_id=?,verifier='',ticket_hash=? WHERE state_hash=?",
            (user_id, forgejo.digest(ticket), row["state_hash"]),
        )
        db.commit()
        success = True
    except (httpx.HTTPError, ValueError, TypeError, HTTPException):
        db.rollback()
        db.execute(
            "UPDATE oauth_flows SET phase='failed',verifier='' WHERE state_hash=?",
            (row["state_hash"],),
        )
        db.commit()
    message = (
        "Вход подтверждён. Вернись в ego-trainer — эту вкладку можно закрыть."
        if success
        else "Вход не завершён. Вернись в ego-trainer и попробуй снова. "
        "Если регистрация закрыта, обратись к наставнику."
    )
    if row["callback_port"] is not None:
        # Callback can only target a local native listener, never an arbitrary origin.
        response = RedirectResponse(
            f"http://127.0.0.1:{row['callback_port']}/callback?"
            + urlencode(
                {"state": state, "ticket": ticket}
                if success
                else {"state": state, "error": "login_failed"}
            ),
            status_code=303,
            headers=_HEADERS,
        )
        response.delete_cookie(_cookie(state), path="/auth/forgejo/callback")
        return response
    nonce = secrets.token_urlsafe(32)
    script = (
        f'<script nonce="{nonce}">const c=new BroadcastChannel("ego-forgejo-{state}");'
        + (
            f'c.postMessage({{ticket:"{ticket}"}});'
            if success
            else 'c.postMessage({error:"login_failed"});'
        )
        + "c.close();</script>"
    )
    response = HTMLResponse(
        '<!doctype html><html lang="ru"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>Ego Trainer</title><body><h1>Ego Trainer</h1><p>"
        + message
        + "</p>"
        + script
        + "</body></html>",
        status_code=200 if success else 400,
        headers={
            **_HEADERS,
            "Content-Security-Policy": f"default-src 'none'; script-src 'nonce-{nonce}'; frame-ancestors 'none'",
        },
    )
    response.delete_cookie(_cookie(state), path="/auth/forgejo/callback")
    return response


@router.post("/forgejo/exchange", response_model=TokenResponse | dict)
async def exchange(body: ExchangeRequest, db: DbDep):
    row = _flow(db, body.state)
    if not secrets.compare_digest(forgejo.challenge(body.code_verifier), row["challenge"]):
        raise HTTPException(status_code=401, detail="Invalid login verifier")
    if row["phase"] == "failed":
        raise HTTPException(
            status_code=400, detail="Forgejo login failed or registration is closed"
        )
    if row["phase"] != "ready":
        return JSONResponse({"pending": True}, status_code=202, headers=_HEADERS)
    if not body.ticket or not secrets.compare_digest(
        forgejo.digest(body.ticket), row["ticket_hash"] or ""
    ):
        raise HTTPException(
            status_code=401, detail="Login must finish in the originating browser or VSCode"
        )
    # Consume only after verifying the client's secret; concurrent exchanges cannot replay.
    consumed = db.execute(
        "DELETE FROM oauth_flows WHERE state_hash=? AND phase='ready' AND expires_at>? RETURNING user_id",
        (row["state_hash"], int(time.time())),
    ).fetchone()
    db.commit()
    if consumed is None:
        raise HTTPException(status_code=400, detail="Login already consumed or expired")
    user = db.execute(
        "SELECT id,username,role FROM students WHERE id=?", (consumed["user_id"],)
    ).fetchone()
    if user is None:
        raise HTTPException(status_code=401, detail="Account no longer exists")
    token = create_token(
        user_id=user["id"],
        username=user["username"],
        role=user["role"],
        expires_in_seconds=load_settings(db).session_minutes * 60,
    )
    return JSONResponse(
        TokenResponse(
            access_token=token, user_id=user["id"], username=user["username"], role=user["role"]
        ).model_dump(),
        headers=_HEADERS,
    )
