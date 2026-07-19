"""Tests for ego_server auth — login, register, me, role checks.

Covers ADR-0001 D8: JWT + roles (student/mentor/admin).

Requires (server/dev extras): fastapi, pyjwt, passlib[bcrypt], httpx.
"""

from __future__ import annotations

import sqlite3

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    """Create an isolated temp SQLite DB and point the server config at it."""
    p = tmp_path / "test.db"
    monkeypatch.setenv("EGO_DB_PATH", str(p))

    # Reload config + db so settings.db_path / get_connection use the temp DB.
    import importlib

    import ego_server.config
    import ego_server.db

    importlib.reload(ego_server.config)
    importlib.reload(ego_server.db)

    from ego_server.db import init_db

    init_db()
    return p


@pytest.fixture
def client(db_path):
    """FastAPI TestClient backed by the temp DB (lifespan inits schema)."""
    import importlib

    import ego_server.main

    importlib.reload(ego_server.main)
    from ego_server.main import app

    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# health
# ---------------------------------------------------------------------------


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# register
# ---------------------------------------------------------------------------


def test_register_returns_token(client):
    r = client.post(
        "/auth/register",
        json={"username": "alice", "password": "secret123", "role": "student"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "student"
    assert data["username"] == "alice"
    assert data["user_id"]


def test_register_duplicate_username_409(client):
    client.post("/auth/register", json={"username": "bob", "password": "p1"})
    r = client.post("/auth/register", json={"username": "bob", "password": "p2"})
    assert r.status_code == 409


def test_register_invalid_role_422(client):
    r = client.post(
        "/auth/register",
        json={"username": "x", "password": "p", "role": "superuser"},
    )
    assert r.status_code == 422  # Pydantic validation error


def test_register_default_role_is_student(client):
    r = client.post("/auth/register", json={"username": "default", "password": "p"})
    assert r.status_code == 200
    assert r.json()["role"] == "student"


# ---------------------------------------------------------------------------
# login
# ---------------------------------------------------------------------------


def test_login_success(client):
    client.post("/auth/register", json={"username": "carol", "password": "pw"})
    r = client.post("/auth/login", json={"username": "carol", "password": "pw"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_wrong_password_401(client):
    client.post("/auth/register", json={"username": "dave", "password": "correct"})
    r = client.post("/auth/login", json={"username": "dave", "password": "wrong"})
    assert r.status_code == 401


def test_login_unknown_user_401(client):
    r = client.post("/auth/login", json={"username": "nobody", "password": "x"})
    assert r.status_code == 401


# ---------------------------------------------------------------------------
# me
# ---------------------------------------------------------------------------


def test_me_with_valid_token(client):
    r = client.post("/auth/register", json={"username": "eve", "password": "p"})
    token = r.json()["access_token"]
    r2 = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    assert r2.json()["username"] == "eve"


def test_me_without_token_401(client):
    r = client.get("/auth/me")
    assert r.status_code == 401


def test_me_with_invalid_token_401(client):
    r = client.get("/auth/me", headers={"Authorization": "Bearer not.a.real.token"})
    assert r.status_code == 401


# ---------------------------------------------------------------------------
# token contents
# ---------------------------------------------------------------------------


def test_token_has_expiry(client):
    import jwt

    from ego_server.config import settings

    r = client.post("/auth/register", json={"username": "exp", "password": "p"})
    token = r.json()["access_token"]
    claims = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    assert "exp" in claims
    assert "iat" in claims
    assert claims["exp"] > claims["iat"]
    assert claims["role"] == "student"
    assert claims["username"] == "exp"


def test_token_role_matches_registered_role(client):
    r = client.post(
        "/auth/register",
        json={"username": "mentor1", "password": "p", "role": "mentor"},
    )
    token = r.json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["role"] == "mentor"


# ---------------------------------------------------------------------------
# password storage
# ---------------------------------------------------------------------------


def test_password_is_hashed_not_stored_plaintext(client, db_path):
    """password_hash in DB is a bcrypt hash, not the plaintext password."""
    client.post(
        "/auth/register",
        json={"username": "hashcheck", "password": "plaintextpw"},
    )
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            "SELECT password_hash FROM students WHERE username = 'hashcheck'"
        ).fetchone()
    finally:
        conn.close()
    assert row
    assert "plaintextpw" not in row[0]
    assert row[0].startswith("$2")  # bcrypt hash format
