"""Integration tests — end-to-end flows on the 33 existing .md tasks.

Complements unit tests in test_parser/test_runner/test_checker by exercising
multi-module flows: parser → models → JSON → models, parser → runner → exec,
parser → stub → syntax check, full-batch parse sanity.
"""

from __future__ import annotations

import ast
import json
from collections import Counter
from pathlib import Path

import pytest

from ego.models import Task
from ego.parser import parse_task_file
from ego.runner import parse_return_value, run_code, run_function


# === Fixtures ===


@pytest.fixture
def parsed_tasks(task_files) -> list[Task]:
    """Parse all 33 .md files into Task objects."""
    return [parse_task_file(p) for p in task_files]


# === Roundtrip: parser → models → JSON → models ===


def test_all_33_serialize_deserialize_roundtrip(parsed_tasks):
    """Every parsed Task should survive JSON roundtrip."""
    for task in parsed_tasks:
        j = task.model_dump_json()
        t2 = Task.model_validate_json(j)
        assert t2.id == task.id
        assert t2.block == task.block
        assert t2.title == task.title
        assert t2.level == task.level
        assert t2.tags == task.tags
        assert t2.statement_md == task.statement_md
        assert t2.stub_py == task.stub_py
        assert t2.solution_py == task.solution_py
        assert t2.content_hash == task.content_hash
        # md_path is Path — serializes to str.
        assert str(t2.md_path) == str(task.md_path)


def test_all_33_json_is_valid_json(parsed_tasks):
    """model_dump_json should produce valid JSON."""
    for task in parsed_tasks:
        j = task.model_dump_json()
        data = json.loads(j)
        assert isinstance(data, dict)
        assert "id" in data
        assert "statement_md" in data


# === Parser → runner → exec reference ===


def test_all_33_reference_solutions_compile(parsed_tasks):
    """Every reference solution should be syntactically valid Python."""
    for task in parsed_tasks:
        try:
            ast.parse(task.solution_py)
        except SyntaxError as e:
            pytest.fail(f"Reference solution for {task.id} has syntax error: {e}")


def test_all_33_stub_compiles(parsed_tasks):
    """Every generated stub should be syntactically valid Python."""
    for task in parsed_tasks:
        try:
            ast.parse(task.stub_py)
        except SyntaxError as e:
            pytest.fail(f"Stub for {task.id} has syntax error: {e}")


def test_all_33_stubs_have_pass(parsed_tasks):
    """Every stub should contain `pass` (the placeholder body)."""
    for task in parsed_tasks:
        assert "pass" in task.stub_py, f"Stub for {task.id} missing 'pass'"


def test_all_33_stubs_exclude_solution_body(parsed_tasks):
    """Stubs should NOT contain the actual reference implementation body."""
    for task in parsed_tasks:
        sol_lines = [
            l.strip()
            for l in task.solution_py.splitlines()
            if l.strip() and not l.strip().startswith("def ")
        ]
        for sol_line in sol_lines:
            if sol_line.startswith('"""') or sol_line.startswith("'''"):
                continue
            if len(sol_line) < 10:
                continue
            assert sol_line not in task.stub_py, (
                f"Stub for {task.id} leaks solution line: {sol_line!r}"
            )


def test_all_33_reference_can_be_run_via_runner(parsed_tasks):
    """Every reference solution should execute (import) without error via runner."""
    for task in parsed_tasks:
        result = run_code(task.solution_py, timeout=3.0)
        assert result.returncode == 0, (
            f"Reference for {task.id} failed to exec: {result.stderr}"
        )
        assert "===EGO_EXCEPTION===" not in result.stderr


# === Block / id uniqueness ===


def test_all_33_ids_unique(parsed_tasks):
    ids = [t.id for t in parsed_tasks]
    assert len(ids) == len(set(ids)), (
        f"Duplicate ids: {[i for i in ids if ids.count(i) > 1]}"
    )


def test_all_33_hashes_unique(parsed_tasks):
    hashes = [t.content_hash for t in parsed_tasks]
    assert len(hashes) == len(set(hashes)), "Duplicate content hashes"


def test_all_33_block_letter_matches_dir(parsed_tasks):
    """Task.block should match the parent dir's block letter."""
    for task in parsed_tasks:
        dir_name = task.md_path.parent.name
        parts = dir_name.split("_")
        if len(parts) >= 2 and parts[0] == "block":
            expected_block = parts[1].upper()
            assert task.block == expected_block, (
                f"{task.id}: block={task.block!r} but dir={dir_name!r} "
                f"suggests {expected_block!r}"
            )


def test_all_33_slug_is_parent_dir(parsed_tasks):
    for task in parsed_tasks:
        assert task.slug == task.md_path.parent.name


def test_all_33_levels_valid(parsed_tasks):
    for task in parsed_tasks:
        assert task.level in ("easy", "medium", "hard"), (
            f"{task.id}: bad level {task.level!r}"
        )


# === Specific tasks: deep checks ===


def test_f1_reference_returns_critical_title(parsed_tasks):
    f1 = next(t for t in parsed_tasks if t.id == "F1")
    result = run_function(
        f1.solution_py,
        "task_f1_find_critical",
        args=(
            [
                {"id": "B1", "severity": "minor", "title": "Typo"},
                {"id": "B2", "severity": "critical", "title": "Crash on login"},
                {"id": "B3", "severity": "minor", "title": "Wrong icon"},
            ],
        ),
        timeout=3.0,
    )
    assert result.returncode == 0
    rv = parse_return_value(result.stdout)
    assert "Crash on login" in rv


def test_f1_reference_returns_empty_for_no_critical(parsed_tasks):
    f1 = next(t for t in parsed_tasks if t.id == "F1")
    result = run_function(
        f1.solution_py,
        "task_f1_find_critical",
        args=([{"severity": "minor", "title": "x"}],),
        timeout=3.0,
    )
    assert result.returncode == 0
    rv = parse_return_value(result.stdout)
    assert rv == "''"  # empty string repr


def test_1_5_reference_sla_report(parsed_tasks):
    """Task 1.5 SLA report — call reference with test data, verify structure."""
    t15 = next(t for t in parsed_tasks if t.id == "1.5")
    logs = [
        {"service": "api", "status": 200},
        {"service": "api", "status": 500},
        {"service": "auth", "status": 200},
        {"service": "auth", "status": 200},
    ]
    result = run_function(
        t15.solution_py,
        "task_1_5_sla_report",
        args=(logs,),
        timeout=3.0,
    )
    assert result.returncode == 0
    rv = parse_return_value(result.stdout)
    assert "'api'" in rv
    assert "'auth'" in rv
    assert "50" in rv  # api sla_percent
    assert "100" in rv  # auth sla_percent


def test_h8_reference_tiered_synthesis(parsed_tasks):
    """H8 cascade synthesis — verify reference computes correctly."""
    h8 = next(t for t in parsed_tasks if t.id == "H8")
    inv = {
        "Iron Ore": {"C": 9, "U": 2, "R": 0},
        "Herb": {"C": 5, "U": 1, "R": 0},
    }
    result = run_function(
        h8.solution_py,
        "task_h8_tiered_synthesis",
        args=(inv,),
        timeout=3.0,
    )
    assert result.returncode == 0
    rv = parse_return_value(result.stdout)
    assert "'C': 0" in rv
    assert "'U': 2" in rv
    assert "'R': 1" in rv


# === Parser robustness ===


def test_parse_each_task_twice_gives_same_hash(parsed_tasks, task_files):
    """Parsing the same .md twice should give identical content_hash."""
    for path, task in zip(task_files, parsed_tasks):
        t2 = parse_task_file(path)
        assert task.content_hash == t2.content_hash, (
            f"{task.id}: hash differs on re-parse"
        )


def test_parse_with_custom_version(parsed_tasks, task_files):
    """parse_task_file accepts default_version and stores it in Task.version."""
    path = task_files[0]
    task = parse_task_file(path, default_version="2.5.0")
    assert task.version == "2.5.0"


# === Runner integration with parser ===


def test_student_stub_returns_none(parsed_tasks):
    """Stub `pass` body should make the function return None."""
    f1 = next(t for t in parsed_tasks if t.id == "F1")
    result = run_function(
        f1.stub_py,
        "task_f1_find_critical",
        args=([{"severity": "critical", "title": "X"}],),
        timeout=2.0,
    )
    rv = parse_return_value(result.stdout)
    # Stub body is `pass` → function returns None → repr is "None".
    assert rv == "None"


# === Block distribution ===


def test_block_distribution(parsed_tasks):
    """Verify expected blocks: 1, A, B, C, D, F, G, H."""
    blocks = {t.block for t in parsed_tasks}
    expected = {"1", "A", "B", "C", "D", "F", "G", "H"}
    assert blocks == expected, (
        f"Unexpected blocks: {blocks - expected} or missing: {expected - blocks}"
    )


def test_block_task_counts(parsed_tasks):
    """Verify task counts per block match the expected distribution."""
    counts = Counter(t.block for t in parsed_tasks)
    expected = {"F": 5, "G": 7, "1": 5, "D": 5, "H": 8, "A": 1, "B": 1, "C": 1}
    for block, count in expected.items():
        assert counts[block] == count, (
            f"Block {block}: expected {count}, got {counts[block]}"
        )


def test_total_task_count(parsed_tasks):
    assert len(parsed_tasks) == 33
