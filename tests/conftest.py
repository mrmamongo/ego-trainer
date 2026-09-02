"""Shared pytest fixtures for ego tests."""

from pathlib import Path

import pytest


@pytest.fixture
def tasks_dir() -> Path:
    """Path to docs/tasks/ with the 33 markdown task files."""
    return Path(__file__).parent.parent / "docs" / "tasks"


@pytest.fixture
def task_files(tasks_dir) -> list[Path]:
    """All .md task files under docs/tasks/."""
    return sorted(tasks_dir.rglob("*.md"))


def create_test_user(client, username: str, password: str, role: str) -> tuple[str, str]:
    """Create a trusted test user directly, then return its login token and ID."""
    from ego_server.auth import generate_user_id, hash_password
    from ego_server.db import get_connection

    conn = get_connection()
    try:
        user_id = generate_user_id()
        pwd_hash = hash_password(password)
        conn.execute(
            "INSERT INTO students (id, username, role, password_hash, created_at) "
            "VALUES (?, ?, ?, ?, datetime('now'))",
            (user_id, username, role, pwd_hash),
        )
        conn.commit()
    finally:
        conn.close()

    response = client.post("/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200, f"login failed for {role}: {response.text}"
    return response.json()["access_token"], user_id
