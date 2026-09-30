"""Forgejo OAuth code exchange and stable local account mapping.

Identity comes from the configured provider's TLS UserInfo endpoint, never
from unverified ID-token claims or a username/email supplied by the client.
"""

from __future__ import annotations

import base64
import hashlib
import sqlite3
from datetime import UTC, datetime
from urllib.parse import urlsplit

import httpx
from fastapi import HTTPException

from ego_server import config
from ego_server.auth import generate_user_id
from ego_server.service_settings import load_settings

FLOW_SECONDS = 300


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("ascii")).hexdigest()


def challenge(verifier: str) -> str:
    return (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest())
        .rstrip(b"=")
        .decode("ascii")
    )


def _base_url(value: str) -> str:
    parts = urlsplit(value)
    loopback = parts.hostname in {"127.0.0.1", "::1", "localhost"}
    if (
        not parts.hostname
        or parts.username is not None
        or parts.password is not None
        or parts.query
        or parts.fragment
        or parts.path not in {"", "/"}
        or (parts.scheme != "https" and not (parts.scheme == "http" and loopback))
    ):
        raise ValueError("OAuth URLs must be HTTPS origins (HTTP only for local development)")
    return value.rstrip("/")


def provider_config() -> tuple[str, str, str]:
    settings = config.settings
    if not settings.forgejo_enabled:
        raise HTTPException(status_code=503, detail="Forgejo login is not configured")
    if not settings.forgejo_client_id or not settings.forgejo_client_secret:
        raise HTTPException(status_code=503, detail="Forgejo login is not configured")
    try:
        issuer = _base_url(settings.forgejo_url)
        public_url = _base_url(settings.public_url)
    except ValueError as exc:
        raise HTTPException(
            status_code=503, detail="Forgejo login configuration is invalid"
        ) from exc
    return issuer, public_url, public_url + "/auth/forgejo/callback"


def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=15, follow_redirects=False, trust_env=False)


async def fetch_identity(code: str, flow: sqlite3.Row) -> tuple[str, str]:
    """Use the provider token only for one authenticated UserInfo request."""
    async with _client() as client:
        response = await client.post(
            flow["issuer"] + "/login/oauth/access_token",
            data={
                "grant_type": "authorization_code",
                "client_id": flow["client_id"],
                "client_secret": config.settings.forgejo_client_secret,
                "redirect_uri": flow["redirect_uri"],
                "code": code,
                "code_verifier": flow["verifier"],
            },
        )
        response.raise_for_status()
        token_data = response.json()
        if not isinstance(token_data, dict):
            raise TypeError("Invalid provider token response")
        token = token_data.get("access_token")
        if not isinstance(token, str) or not token or len(token) > 32767:
            raise ValueError("Invalid provider token response")
        response = await client.get(
            flow["issuer"] + "/login/oauth/userinfo",
            headers={"Authorization": "Bearer " + token},
        )
        response.raise_for_status()
        profile = response.json()
        if not isinstance(profile, dict):
            raise TypeError("Invalid provider identity response")
        subject = profile.get("sub")
        name = profile.get("preferred_username")
        if (
            not isinstance(subject, str)
            or not subject
            or len(subject) > 255
            or not subject.isascii()
            or any(ord(char) < 33 for char in subject)
            or not isinstance(name, str)
            or not name.strip()
            or len(name) > 255
        ):
            raise ValueError("Invalid provider identity response")
        return subject, name


def resolve_user(db: sqlite3.Connection, issuer: str, subject: str, name: str) -> str:
    """Resolve issuer + subject, creating a student only when registration is open.

    Caller owns a short write transaction. No provider network calls happen here.
    Existing local roles and progress remain authoritative.
    """
    identity = db.execute(
        "SELECT user_id FROM external_identities WHERE issuer=? AND subject=?", (issuer, subject)
    ).fetchone()
    now = datetime.now(UTC).isoformat()
    if identity:
        user_id = identity["user_id"]
        db.execute(
            "UPDATE external_identities SET remote_username=? WHERE issuer=? AND subject=?",
            (name, issuer, subject),
        )
    else:
        if not load_settings(db).registration_enabled:
            raise HTTPException(status_code=403, detail="Registration is disabled")
        user_id = generate_user_id()
        username = name
        if db.execute("SELECT 1 FROM students WHERE username=?", (username,)).fetchone():
            username = "forgejo-" + user_id
        db.execute(
            "INSERT INTO students (id,username,role,password_hash,created_at) VALUES (?,?,?,?,?)",
            (user_id, username, "student", "", now),
        )
        db.execute(
            "INSERT INTO external_identities (issuer,subject,user_id,remote_username,created_at) "
            "VALUES (?,?,?,?,?)",
            (issuer, subject, user_id, name, now),
        )
    db.execute("UPDATE students SET last_login_at=? WHERE id=?", (now, user_id))
    return user_id
