"""FastAPI dependencies.

Реализация — в задаче ego-trainer-bmh.2 (Auth) и далее. Сейчас заглушки.
"""

import sqlite3
from typing import Annotated

from fastapi import Depends, HTTPException, status

from ego_server.db import get_connection


def get_db() -> sqlite3.Connection:
    """Yields a SQLite connection. NOT a real dependency yet — placeholder."""
    # В реальной реализации будет yield + close
    return get_connection()


DbDep = Annotated[sqlite3.Connection, Depends(get_db)]


def get_current_user() -> dict:
    """Placeholder — returns a fake student. Real impl in bmh.2."""
    return {"id": "fake-student-id", "username": "fake", "role": "student"}


CurrentUser = Annotated[dict, Depends(get_current_user)]


def require_role(*roles: str):
    """Dependency factory: require one of the given roles. Real impl in bmh.2."""
    def _check(user: CurrentUser) -> dict:
        if user["role"] not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
        return user
    return _check
