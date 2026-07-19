"""Auth router: login, register, me.

Per ADR-0001 D8: JWT + roles (student/mentor/admin).
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from ego_server.auth import create_token, generate_user_id, hash_password, verify_password
from ego_server.deps import DbDep, TokenDep
from ego_server.models import LoginRequest, MeResponse, RegisterRequest, TokenResponse


router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: DbDep) -> TokenResponse:
    """Login with username/password, receive a JWT."""
    row = db.execute(
        "SELECT id, username, role, password_hash FROM students WHERE username = ?",
        (body.username,),
    ).fetchone()
    if not row or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_token(user_id=row["id"], username=row["username"], role=row["role"])
    return TokenResponse(
        access_token=token,
        role=row["role"],
        username=row["username"],
        user_id=row["id"],
    )


@router.post("/register", response_model=TokenResponse)
async def register(body: RegisterRequest, db: DbDep) -> TokenResponse:
    """Register a new user. Returns a token immediately (no email verification in MVP)."""
    existing = db.execute(
        "SELECT id FROM students WHERE username = ?", (body.username,)
    ).fetchone()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )
    user_id = generate_user_id()
    pwd_hash = hash_password(body.password)
    db.execute(
        "INSERT INTO students (id, username, role, password_hash, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (user_id, body.username, body.role, pwd_hash, _now_iso()),
    )
    db.commit()
    token = create_token(user_id=user_id, username=body.username, role=body.role)
    return TokenResponse(
        access_token=token,
        role=body.role,
        username=body.username,
        user_id=user_id,
    )


@router.get("/me", response_model=MeResponse)
async def me(token: TokenDep) -> MeResponse:
    """Return the current user parsed from the JWT."""
    return MeResponse(
        user_id=token["sub"],
        username=token["username"],
        role=token["role"],
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
