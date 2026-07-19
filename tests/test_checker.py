"""Tests for ego.checker — comparing student solution to reference."""

from __future__ import annotations

from pathlib import Path

import pytest

from ego.checker import (
    CheckResult,
    TestCase,
    TestResult,
    _find_main_function,
    _safe_repr,
    format_check_result,
    run_check,
)
from ego.models import Task


# === Helpers ===


def _make_task(
    solution_py: str,
    *,
    statement_md: str = "# stub",
    stub_py: str = "def task_x():\n    pass\n",
    tests_code: str = "",
    task_id: str = "X1",
    block: str = "X",
) -> Task:
    extra = {"tests_code": tests_code} if tests_code else {}
    return Task(
        id=task_id,
        block=block,
        slug="block_x",
        task_id=task_id,
        title="Test",
        level="easy",
        md_path=Path("test.md"),
        statement_md=statement_md,
        stub_py=stub_py,
        solution_py=solution_py,
        extra=extra,
    )


# === _find_main_function ===


def test_find_main_function_basic():
    code = "def task_x(a):\n    return a + 1\n"
    assert _find_main_function(code) == "task_x"


def test_find_main_function_with_helper():
    code = (
        "def _helper(x):\n    return x * 2\n\n"
        "def task_main(n):\n    return _helper(n) + 1\n"
    )
    assert _find_main_function(code) == "task_main"


def test_find_main_function_no_task_func():
    code = "def f(x):\n    return x\n"
    assert _find_main_function(code) is None


def test_find_main_function_invalid_syntax():
    assert _find_main_function("def task_x( :") is None


def test_find_main_function_empty():
    assert _find_main_function("") is None


# === _safe_repr ===


def test_safe_repr_int():
    assert _safe_repr(42) == "42"


def test_safe_repr_string():
    assert _safe_repr("hello") == "'hello'"


def test_safe_repr_list():
    assert _safe_repr([1, 2, 3]) == "[1, 2, 3]"


def test_safe_repr_dict():
    r = _safe_repr({"a": 1})
    assert "'a': 1" in r


# === run_check: basic ===


def test_run_check_correct_solution():
    task = _make_task(
        solution_py="def task_x(n):\n    return n * 2\n",
        tests_code='[(5, 10, "double 5"), (0, 0, "zero"), (-3, -6, "negative")]',
    )
    student = "def task_x(n):\n    return n * 2\n"
    result = run_check(task, student)
    assert result.status == "passed"
    assert result.passed_tests == 3
    assert result.total_tests == 3
    assert result.all_passed


def test_run_check_wrong_solution():
    task = _make_task(
        solution_py="def task_x(n):\n    return n * 2\n",
        tests_code='[(5, 10, "double 5")]',
    )
    student = "def task_x(n):\n    return n + 2\n"  # wrong
    result = run_check(task, student)
    assert result.status == "failed"
    assert result.passed_tests == 0
    assert result.total_tests == 1
    assert not result.all_passed
    assert not result.results[0].passed
    assert "10" in result.results[0].expected_repr
    assert "7" in result.results[0].actual_repr  # 5+2=7


def test_run_check_partial_pass():
    task = _make_task(
        solution_py="def task_x(n):\n    return n * 2\n",
        tests_code='[(5, 10, "double 5"), (0, 1, "wrong expected"), (-3, -6, "negative")]',
    )
    student = "def task_x(n):\n    return n * 2\n"
    # Middle test has intentionally wrong expected value in tests_code.
    result = run_check(task, student)
    assert result.status == "partial"
    assert result.passed_tests == 2
    assert result.total_tests == 3


# === run_check: edge cases ===


def test_run_check_no_tests():
    task = _make_task(
        solution_py="def task_x(n):\n    return n * 2\n",
        tests_code="",  # no tests
    )
    student = "def task_x(n):\n    return n * 2\n"
    result = run_check(task, student)
    assert result.status == "no_tests"
    assert result.total_tests == 0


def test_run_check_student_timeout():
    task = _make_task(
        solution_py="def task_x(n):\n    return n * 2\n",
        tests_code='[(5, 10, "double 5")]',
    )
    student = "def task_x(n):\n    while True:\n        pass\n"
    result = run_check(task, student, timeout=2.0)
    assert result.status == "timeout"
    assert result.passed_tests == 0


def test_run_check_student_exception():
    task = _make_task(
        solution_py="def task_x(n):\n    return n * 2\n",
        tests_code='[(5, 10, "double 5")]',
    )
    student = "def task_x(n):\n    raise ValueError('boom')\n"
    result = run_check(task, student)
    assert result.status == "error"
    assert result.passed_tests == 0
    assert "ValueError" in (result.results[0].error or "")


def test_run_check_student_no_return():
    """`pass` returns None — repr(None)='None' is a valid (wrong) value → failed."""
    task = _make_task(
        solution_py="def task_x(n):\n    return n * 2\n",
        tests_code='[(5, 10, "double 5")]',
    )
    student = "def task_x(n):\n    pass\n"  # returns None
    result = run_check(task, student)
    # None != 10 → test fails (not an error, just wrong value).
    assert result.status == "failed"
    assert result.passed_tests == 0
    assert result.results[0].actual_repr == "None"


def test_run_check_student_syntax_error():
    task = _make_task(
        solution_py="def task_x(n):\n    return n * 2\n",
        tests_code='[(5, 10, "double 5")]',
    )
    student = "def task_x(n)\n    return n * 2\n"  # missing colon
    result = run_check(task, student)
    assert result.status == "error"


def test_run_check_solution_hash_computed():
    task = _make_task(
        solution_py="def task_x(n):\n    return n * 2\n",
        tests_code='[(5, 10, "double 5")]',
    )
    student = "def task_x(n):\n    return n * 2\n"
    result = run_check(task, student)
    assert result.solution_hash
    assert len(result.solution_hash) == 64  # sha256 hex


def test_run_check_no_main_function_in_solution():
    task = _make_task(
        solution_py="def helper():\n    return 42\n",  # no task_* function
        tests_code='[(5, 10, "test")]',
    )
    student = "def task_x(n):\n    return n * 2\n"
    result = run_check(task, student)
    assert result.status == "error"
    assert result.total_tests == 0


# === Multi-arg functions ===


def test_run_check_multi_arg_with_tuple_input():
    task = _make_task(
        solution_py="def task_add(a, b):\n    return a + b\n",
        tests_code='[((2, 3), 5, "add 2+3"), ((10, -5), 5, "add 10+-5")]',
    )
    student = "def task_add(a, b):\n    return a + b\n"
    result = run_check(task, student)
    assert result.status == "passed"
    assert result.passed_tests == 2


def test_run_check_dict_return():
    task = _make_task(
        solution_py=(
            "def task_count(items):\n"
            "    r = {}\n"
            "    for x in items:\n"
            "        r[x] = r.get(x, 0) + 1\n"
            "    return r\n"
        ),
        tests_code='[(["a", "b", "a"], {"a": 2, "b": 1}, "count letters")]',
    )
    student = task.solution_py
    result = run_check(task, student)
    assert result.status == "passed"


# === format_check_result ===


def test_format_passed():
    task = _make_task(
        solution_py="def task_x(n):\n    return n * 2\n",
        tests_code='[(5, 10, "test")]',
    )
    student = "def task_x(n):\n    return n * 2\n"
    result = run_check(task, student)
    out = format_check_result(result)
    assert "PASSED" in out
    assert "1/1" in out


def test_format_failed():
    task = _make_task(
        solution_py="def task_x(n):\n    return n * 2\n",
        tests_code='[(5, 10, "test")]',
    )
    student = "def task_x(n):\n    return n + 2\n"
    result = run_check(task, student)
    out = format_check_result(result)
    assert "FAILED" in out


def test_format_no_tests():
    task = _make_task(solution_py="def task_x():\n    return 0\n", tests_code="")
    result = run_check(task, "def task_x():\n    return 0\n")
    out = format_check_result(result)
    assert "NO_TESTS" in out


# === Real .md tasks (33 from docs/tasks/) ===


def test_run_check_real_f1_no_tests_status():
    """Existing 33 .md don't have ## Тесты — so status=no_tests."""
    from ego.parser import parse_task_file

    path = Path(__file__).parent.parent / "docs" / "tasks" / "block_f_simple" / "task_f1.md"
    task = parse_task_file(path)
    if not task.extra.get("tests_code"):
        result = run_check(task, task.stub_py)
        assert result.status == "no_tests"


def test_run_check_real_f1_with_tests_added():
    """If we add tests_code manually, the reference solution should pass itself."""
    from ego.parser import parse_task_file

    path = Path(__file__).parent.parent / "docs" / "tasks" / "block_f_simple" / "task_f1.md"
    task = parse_task_file(path)
    task_with_tests = task.model_copy(
        update={
            "extra": {
                **task.extra,
                "tests_code": (
                    '([(\n'
                    '  [{"severity": "minor", "title": "x"},\n'
                    '   {"severity": "critical", "title": "BOOM"}],\n'
                    '  "BOOM", "has critical")\n'
                    '])'
                ),
            }
        }
    )
    # Stub doesn't return BOOM — it returns None.
    result = run_check(task_with_tests, task_with_tests.stub_py)
    assert result.status in ("error", "failed")
    # The reference solution should pass itself.
    result = run_check(task_with_tests, task_with_tests.solution_py)
    assert result.status == "passed"
