"""Checker — compares student's solution to reference, runs test cases.

Используется ego.cli.check_cmd для:
  1. Загрузки Task (из .md через parser или из .ego/cache/ после pull)
  2. Загрузки student.py (из tasks/<block>/<task>.py)
  3. run_check(task, student_code) -> CheckResult

Сравнивает решение студента с эталоном на наборе тестовых кейсов.
Кейсы берутся из Task.extra["tests_code"] (явные кортежи), либо
из единственного примера (fallback), либо проверка отказывает.

See ADR-0001 D12 (sandbox), D9 (сервер не выполняет код — check локален),
D15 (тесты в .md).
"""

from __future__ import annotations

import ast
import dataclasses
import hashlib
from typing import Any

from ego.models import Task
from ego.runner import parse_return_value, run_function


@dataclasses.dataclass
class TestCase:
    """Один тестовый кейс: (args, kwargs, expected_repr, description)."""

    __test__ = False  # not a pytest test class

    args: tuple
    kwargs: dict
    expected_repr: str
    description: str


@dataclasses.dataclass
class TestResult:
    """Результат одного теста."""

    __test__ = False  # not a pytest test class

    description: str
    passed: bool
    expected_repr: str
    actual_repr: str | None
    error: str | None = None  # traceback if student code raised


@dataclasses.dataclass
class CheckResult:
    """Итог проверки задачи: список результатов + сводка."""

    task_id: str
    version: str
    passed_tests: int
    total_tests: int
    status: str  # "passed" | "partial" | "failed" | "error" | "timeout" | "no_tests"
    results: list[TestResult]
    student_code: str
    solution_hash: str  # sha256(student_code)

    @property
    def all_passed(self) -> bool:
        return self.passed_tests == self.total_tests and self.total_tests > 0


def run_check(
    task: Task,
    student_code: str,
    *,
    timeout: float = 5.0,
) -> CheckResult:
    """Run student's solution against test cases, compare with reference.

    Args:
        task: Task with solution_py (reference), extra["tests_code"] (optional).
        student_code: Student's Python source (should define task_* function).
        timeout: Per-test timeout in seconds.

    Returns:
        CheckResult with per-test results and summary.

    Steps:
        1. Find the main function name (task_*) in solution_py.
        2. Extract test cases from task.extra["tests_code"] or fallback to example.
        3. For each test case:
            a. Run reference function with test args -> expected_repr
            b. Run student function with same args -> actual_repr
            c. Compare reprs -> passed/failed
        4. Aggregate into CheckResult.
    """
    func_name = _find_main_function(task.solution_py)
    if not func_name:
        return CheckResult(
            task_id=task.id,
            version=task.version,
            passed_tests=0,
            total_tests=0,
            status="error",
            results=[],
            student_code=student_code,
            solution_hash=_hash_code(student_code),
        )

    test_cases = _extract_test_cases(task)
    if not test_cases:
        return CheckResult(
            task_id=task.id,
            version=task.version,
            passed_tests=0,
            total_tests=0,
            status="no_tests",
            results=[],
            student_code=student_code,
            solution_hash=_hash_code(student_code),
        )

    results: list[TestResult] = []
    passed_count = 0
    had_timeout = False
    had_error = False

    for tc in test_cases:
        # expected_repr comes from tests_code (explicit expected value).
        expected_repr = tc.expected_repr

        # Run student.
        stu_result = run_function(
            student_code,
            func_name,
            args=tc.args,
            kwargs=tc.kwargs,
            timeout=timeout,
        )

        if stu_result.timed_out:
            had_timeout = True
            results.append(
                TestResult(
                    description=tc.description,
                    passed=False,
                    expected_repr=expected_repr,
                    actual_repr=None,
                    error="TIMEOUT",
                )
            )
            continue

        if stu_result.exception or stu_result.returncode != 0:
            had_error = True
            err_lines = stu_result.stderr.splitlines()
            err_msg = "\n".join(err_lines[:10]) if err_lines else "unknown error"
            results.append(
                TestResult(
                    description=tc.description,
                    passed=False,
                    expected_repr=expected_repr,
                    actual_repr=None,
                    error=err_msg,
                )
            )
            continue

        actual_repr = parse_return_value(stu_result.stdout)
        if actual_repr is None:
            had_error = True
            results.append(
                TestResult(
                    description=tc.description,
                    passed=False,
                    expected_repr=expected_repr,
                    actual_repr=None,
                    error="no return value (function returned None?)",
                )
            )
            continue

        passed = actual_repr == expected_repr
        if passed:
            passed_count += 1
        results.append(
            TestResult(
                description=tc.description,
                passed=passed,
                expected_repr=expected_repr,
                actual_repr=actual_repr,
            )
        )

    # Determine overall status.
    total = len(results)
    if had_timeout and passed_count == 0:
        status = "timeout"
    elif had_error and passed_count == 0:
        status = "error"
    elif passed_count == total and total > 0:
        status = "passed"
    elif passed_count == 0:
        status = "failed"
    else:
        status = "partial"

    return CheckResult(
        task_id=task.id,
        version=task.version,
        passed_tests=passed_count,
        total_tests=total,
        status=status,
        results=results,
        student_code=student_code,
        solution_hash=_hash_code(student_code),
    )


# === Helpers ===


def _find_main_function(code: str) -> str | None:
    """Find the main task_* function name in Python source.

    Returns the first ``def task_<name>`` found, or ``None``.
    Excludes helper functions (those starting with ``_``).
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("task_"):
            return node.name
    return None


def _extract_test_cases(task: Task) -> list[TestCase]:
    """Extract test cases from ``task.extra["tests_code"]``.

    - If ``tests_code`` exists: parse it as a Python literal (list of tuples).
      Each tuple is ``(input, expected, description)`` or ``(input, expected)``.
      For multi-arg functions, ``input`` is a tuple itself.
    - Otherwise: return empty list (caller handles ``no_tests`` status).
    """
    tests_code = task.extra.get("tests_code", "").strip()
    if not tests_code:
        return []

    # Parse tests_code as a Python literal — safe (no calls/lambda allowed).
    try:
        tree = ast.parse(tests_code, mode="eval")
        cases_raw = ast.literal_eval(tree.body)
    except Exception:
        return []

    if not isinstance(cases_raw, list):
        return []

    cases: list[TestCase] = []
    for entry in cases_raw:
        if not isinstance(entry, (tuple, list)):
            continue
        if len(entry) == 3:
            inp, _expected, desc = entry
        elif len(entry) == 2:
            inp, _expected = entry
            desc = "test"
        else:
            continue

        # inp may be a single value or a tuple of args.
        if isinstance(inp, tuple):
            args = inp
        else:
            args = (inp,)
        kwargs: dict = {}

        # expected_repr computed via _safe_repr (value is from our own code).
        expected_repr = _safe_repr(_expected)

        cases.append(
            TestCase(
                args=args,
                kwargs=kwargs,
                expected_repr=expected_repr,
                description=str(desc),
            )
        )

    return cases


def _safe_repr(value: Any) -> str:
    """Compute repr of a value. Value comes from our own code (trusted)."""
    return repr(value)


def _hash_code(code: str) -> str:
    """sha256 hex digest of student code (utf-8)."""
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def format_check_result(result: CheckResult) -> str:
    """Human-readable summary of a CheckResult for CLI output."""
    icons = {
        "passed": "OK",
        "partial": "PARTIAL",
        "failed": "FAIL",
        "error": "ERROR",
        "timeout": "TIMEOUT",
        "no_tests": "NO_TESTS",
    }
    icon = icons.get(result.status, "?")
    lines = [
        f"[{icon}] Задача {result.task_id} (v{result.version}): {result.status.upper()}",
        f"   Пройдено тестов: {result.passed_tests}/{result.total_tests}",
    ]
    for tr in result.results:
        if tr.passed:
            lines.append(f"   + {tr.description}")
        else:
            lines.append(f"   x {tr.description}")
            lines.append(f"     Ожидалось: {tr.expected_repr}")
            if tr.actual_repr is not None:
                lines.append(f"     Получилось: {tr.actual_repr}")
            if tr.error:
                err_short = tr.error.split("\n")[0][:200]
                lines.append(f"     Ошибка: {err_short}")
    return "\n".join(lines)
