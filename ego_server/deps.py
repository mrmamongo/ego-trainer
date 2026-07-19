"""FastAPI dependencies: DB connection, JWT auth, role-based access.

Per ADR-0001 D8: JWT + roles (student/mentor/admin).
"""

from __future__ import annotations

import sqlite3
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ego_server.auth import decode_token
from ego_server.db import get_connection


# auto_error=False so we can produce a clean 401 with WWW-Authenticate header.
_bearer = HTTPBearer(auto_error=False)


def get_db() -> sqlite3.Connection:
    """Yield a SQLite connection and close it after the request."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


DbDep = Annotated[sqlite3.Connection, Depends(get_db)]


def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> dict:
    """Verify JWT from ``Authorization: Bearer <token>`` and return claims.

    Raises 401 if the header is missing, malformed, or the token is invalid/expired.
    """
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        claims = decode_token(creds.credentials)
    except Exception as e:  # noqa: BLE001 - any token error -> 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return claims


CurrentUser = Annotated[dict, Depends(get_current_user)]

# Alias for endpoints that need just the token claims (read-only).
TokenDep = CurrentUser


def require_role(*roles: str):
    """Dependency factory: require the caller to have one of *roles*.

    Usage::

        @router.get(
            "/mentor-only",
            dependencies=[Depends(require_role("mentor", "admin"))],
        )
        async def handler(...): ...
    """
    def _check(user: CurrentUser) -> dict:
        if user["role"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role: {', '.join(roles)}",
            )
        return user

    return _check
