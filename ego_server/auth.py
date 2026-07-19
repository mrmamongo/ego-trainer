"""Auth utilities: password hashing (bcrypt), JWT token generation/verification.

Per ADR-0001 D8: JWT + roles (student/mentor/admin).
"""

from __future__ import annotations

import secrets
import time
from typing import Any

import jwt
from passlib.context import CryptContext

from ego_server.config import settings


_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return _pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    return _pwd_context.verify(plain, hashed)


def create_token(
    *,
    user_id: str,
    username: str,
    role: str,
    expires_in_seconds: int | None = None,
) -> str:
    """Create a JWT token for a user.

    Claims: sub (user_id), username, role, iat, exp.
    """
    if expires_in_seconds is None:
        expires_in_seconds = settings.jwt_expire_minutes * 60
    now = int(time.time())
    payload: dict[str, Any] = {
        "sub": user_id,
        "username": username,
        "role": role,
        "iat": now,
        "exp": now + expires_in_seconds,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT token. Returns claims dict.

    Raises:
        jwt.ExpiredSignatureError: token expired
        jwt.InvalidTokenError: invalid signature/malformed
    """
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


def generate_user_id() -> str:
    """Generate a random user ID (32 hex chars / 128 bits)."""
    return secrets.token_hex(16)
