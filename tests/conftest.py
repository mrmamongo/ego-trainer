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
