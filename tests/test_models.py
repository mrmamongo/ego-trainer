"""Tests for ego.models — Pydantic v2 data models."""

import json
from datetime import datetime
from pathlib import Path

import pytest

from ego.models import (
    Config,
    Level,
    Manifest,
    ManifestTaskEntry,
    Progress,
    ProgressEntry,
    Role,
    Run,
    RunStatus,
    Task,
    TaskStatus,
)


def test_task_basic():
    t = Task(
        id="F1", block="F", slug="block_f_simple", task_id="F1",
        title="Test", level="easy", md_path=Path("docs/tasks/F1.md"),
        statement_md="# F1\n...", stub_py="def f():\n    pass\n",
        solution_py="def f():\n    return 42\n",
    )
    assert t.id == "F1"
    assert t.level == "easy"
    assert t.tags == []


def test_task_serializes_to_json():
    t = Task(
        id="F1", block="F", slug="block_f_simple", task_id="F1",
        title="T", level="medium", md_path=Path("x.md"),
        statement_md="x", stub_py="x", solution_py="x",
    )
    j = t.model_dump_json()
    data = json.loads(j)
    assert data["id"] == "F1"
    assert data["md_path"] == "x.md"  # Path → str


def test_progress_upsert_insert():
    p = Progress()
    e = ProgressEntry(task_id="F1", version="1.0.0")
    p.upsert(e)
    assert len(p.entries) == 1
    assert p.find("F1", "1.0.0") is e


def test_progress_upsert_update():
    p = Progress()
    p.upsert(ProgressEntry(task_id="F1", version="1.0.0", attempts=1))
    p.upsert(ProgressEntry(task_id="F1", version="1.0.0", attempts=2, status="passed", passed_tests=3, total_tests=3))
    assert len(p.entries) == 1
    assert p.entries[0].attempts == 2
    assert p.entries[0].status == "passed"


def test_progress_find_missing():
    p = Progress()
    assert p.find("X1", "1.0.0") is None


def test_config_defaults():
    c = Config()
    assert c.server_url == "http://localhost:8000"
    assert c.role == "student"
    assert c.sandbox_timeout_sec == 5.0


def test_config_roundtrip():
    c = Config(server_url="http://ego.example.com", token="abc", student_username="ivan", role="mentor")
    j = c.model_dump_json()
    c2 = Config.model_validate_json(j)
    assert c2 == c


def test_manifest_with_entries():
    m = Manifest(
        tasks=[
            ManifestTaskEntry(
                id="F1", block="F", slug="block_f_simple",
                version="1.0.0", content_hash="abc",
                pulled_at=datetime(2026, 7, 19, 12, 0, 0),
                md_path="tasks/F/F1.md",
            ),
        ],
        last_pull_at=datetime(2026, 7, 19, 12, 0, 0),
    )
    j = m.model_dump_json()
    m2 = Manifest.model_validate_json(j)
    assert m2.tasks[0].id == "F1"
    assert m2.tasks[0].pulled_at == datetime(2026, 7, 19, 12, 0, 0)


def test_run_with_error():
    r = Run(
        id="r1", task_id="F1", version="1.0.0",
        started_at=datetime(2026, 7, 19, 12, 0, 0),
        status="error", error="SyntaxError: ...",
    )
    assert r.status == "error"
    assert "SyntaxError" in r.error


def test_level_invalid_raises():
    with pytest.raises(Exception):
        Task(
            id="X", block="X", slug="x", task_id="X", title="t",
            level="impossible",  # невалидный Literal
            md_path=Path("x.md"), statement_md="x", stub_py="x", solution_py="x",
        )
