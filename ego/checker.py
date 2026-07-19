"""Checker — compares student's solution to reference, runs test cases.

Cases from (in order):
  1. ``Task.tests_file`` (``.tests.py`` with ``@case`` / hooks) — preferred
  2. Legacy ``Task.extra["tests_code"]`` (``ast.literal_eval``, level=smoke)

Level filter (``smoke`` | ``full`` | ``all``, default ``smoke``):
  see docs/TESTS_DESIGN.md. Hypothesis / property — epic 9u7 (full corpus).

See ADR-0001 D12 (sandbox), D9, D15; docs/TESTS_DESIGN.md.
"""

from __future__ import annotations

import ast
import dataclasses
import hashlib
import importlib.util
import sys
from pathlib import Path
from typing import Any, Callable

from ego.models import Task
from ego.runner import parse_return_value, run_function
from ego.testing import (
    CaseResult,
    LevelFilter,
    TestCase as EgoTestCase,
    TestLevel,
    case_matches_filter,
)


@dataclasses.dataclass
class TestCase:
    """Runtime test case used by ``run_check``."""

    __test__ = False  # not a pytest test class

    args: tuple
    kwargs: dict
    expected_repr: str
    description: str
    level: TestLevel = "smoke"


@dataclasses.dataclass
class TestResult:
    """Результат одного теста."""

    __test__ = False  # not a pytest test class

    description: str
    passed: bool
    expected_repr: str
    actual_repr: str | None
    error: str | None = None  # traceback if student code raised
    level: TestLevel = "smoke"


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
    level: LevelFilter = "smoke"  # filter that was requested

    @property
    def all_passed(self) -> bool:
        return self.passed_tests == self.total_tests and self.total_tests > 0


def run_check(
    task: Task,
    student_code: str,
    *,
    timeout: float = 5.0,
    level: LevelFilter = "smoke",
) -> CheckResult:
    """Run student's solution against test cases, compare with expected.

    Args:
        task: Task with solution_py / tests_file / extra["tests_code"].
        student_code: Student's Python source (should define task_* function).
        timeout: Per-test timeout in seconds.
        level: Which cases to run — ``smoke`` (default), ``full``, or ``all``.
    """
    if level not in ("smoke", "full", "all"):
        raise ValueError(f"invalid level filter: {level!r}")

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
            level=level,
        )

    loaded = _load_tests_module(task)
    test_cases = _extract_test_cases(task, level=level, loaded=loaded)
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
            level=level,
        )

    before_hook, after_hook = _find_hooks(loaded)
    # task_func stub for hooks — mentor hooks may inspect signature/name.
    task_func = _make_task_func_stub(func_name)

    results: list[TestResult] = []
    passed_count = 0
    had_timeout = False
    had_error = False

    for tc in test_cases:
        expected_repr = tc.expected_repr
        ctx: dict = {}
        if before_hook is not None:
            try:
                ctx_raw = before_hook(task_func)
                ctx = ctx_raw if isinstance(ctx_raw, dict) else {}
            except Exception as exc:  # noqa: BLE001
                had_error = True
                results.append(
                    TestResult(
                        description=tc.description,
                        passed=False,
                        expected_repr=expected_repr,
                        actual_repr=None,
                        error=f"@before failed: {exc}",
                        level=tc.level,
                    )
                )
                continue

        stu_result = run_function(
            student_code,
            func_name,
            args=tc.args,
            kwargs=tc.kwargs,
            timeout=timeout,
        )

        if stu_result.timed_out:
            had_timeout = True
            tr = TestResult(
                description=tc.description,
                passed=False,
                expected_repr=expected_repr,
                actual_repr=None,
                error="TIMEOUT",
                level=tc.level,
            )
            results.append(tr)
            _call_after(after_hook, task_func, tr, ctx)
            continue

        if stu_result.exception or stu_result.returncode != 0:
            had_error = True
            err_lines = stu_result.stderr.splitlines()
            err_msg = "\n".join(err_lines[:10]) if err_lines else "unknown error"
            tr = TestResult(
                description=tc.description,
                passed=False,
                expected_repr=expected_repr,
                actual_repr=None,
                error=err_msg,
                level=tc.level,
            )
            results.append(tr)
            _call_after(after_hook, task_func, tr, ctx)
            continue

        actual_repr = parse_return_value(stu_result.stdout)
        if actual_repr is None:
            had_error = True
            tr = TestResult(
                description=tc.description,
                passed=False,
                expected_repr=expected_repr,
                actual_repr=None,
                error="no return value (function returned None?)",
                level=tc.level,
            )
            results.append(tr)
            _call_after(after_hook, task_func, tr, ctx)
            continue

        passed = actual_repr == expected_repr
        if passed:
            passed_count += 1
        tr = TestResult(
            description=tc.description,
            passed=passed,
            expected_repr=expected_repr,
            actual_repr=actual_repr,
            level=tc.level,
        )
        results.append(tr)
        _call_after(after_hook, task_func, tr, ctx)

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
        level=level,
    )


# === Helpers ===


def _find_main_function(code: str) -> str | None:
    """Find the main task_* function name in Python source."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("task_"):
            return node.name
    return None


def _make_task_func_stub(func_name: str) -> Callable:
    """Minimal callable with the right ``__name__`` for hooks."""

    def stub(*_a: Any, **_k: Any) -> None:
        return None

    stub.__name__ = func_name
    return stub


def _call_after(
    after_hook: Callable | None,
    task_func: Callable,
    tr: TestResult,
    ctx: dict,
) -> None:
    if after_hook is None:
        return
    case_result = CaseResult(
        description=tr.description,
        passed=tr.passed,
        expected_repr=tr.expected_repr,
        actual_repr=tr.actual_repr,
        error=tr.error,
        level=tr.level,
    )
    try:
        after_hook(task_func, case_result, ctx)
    except Exception:  # noqa: BLE001
        pass  # after failures must not mask the case result


@dataclasses.dataclass
class _LoadedTests:
    """Imported ``.tests.py`` module + collected cases/hooks."""

    module: Any
    cases: list[EgoTestCase]
    before_hook: Callable | None
    after_hook: Callable | None


def _load_tests_module(task: Task) -> _LoadedTests | None:
    """Import ``task.tests_file`` via importlib; return None if absent."""
    path = task.tests_file
    if path is None or not Path(path).is_file():
        return None

    path = Path(path)
    mod_name = f"ego_task_tests_{path.stem.replace('.', '_')}_{_hash_code(str(path))[:8]}"
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    # Ensure ego.testing is importable (package already installed in normal runs).
    sys.modules[mod_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:  # noqa: BLE001
        sys.modules.pop(mod_name, None)
        return None

    cases: list[EgoTestCase] = []
    before_hook: Callable | None = None
    after_hook: Callable | None = None

    for name in dir(module):
        obj = getattr(module, name)
        if callable(obj) and getattr(obj, "_ego_before", False):
            before_hook = obj
        if callable(obj) and getattr(obj, "_ego_after", False):
            after_hook = obj
        if callable(obj) and name.startswith("task_") and hasattr(obj, "_ego_cases"):
            cases.extend(obj._ego_cases)

    return _LoadedTests(
        module=module,
        cases=cases,
        before_hook=before_hook,
        after_hook=after_hook,
    )


def _find_hooks(
    loaded: _LoadedTests | None,
) -> tuple[Callable | None, Callable | None]:
    if loaded is None:
        return None, None
    return loaded.before_hook, loaded.after_hook


def _extract_test_cases(
    task: Task,
    *,
    level: LevelFilter,
    loaded: _LoadedTests | None,
) -> list[TestCase]:
    """Extract + filter cases from ``.tests.py`` or legacy ``tests_code``."""
    if loaded is not None and loaded.cases:
        out: list[TestCase] = []
        for ec in loaded.cases:
            if not case_matches_filter(ec.level, level):
                continue
            out.append(
                TestCase(
                    args=ec.args if isinstance(ec.args, tuple) else (ec.args,),
                    kwargs={},
                    expected_repr=_safe_repr(ec.expected),
                    description=ec.description or "test",
                    level=ec.level,
                )
            )
        return out

    # Legacy ## Тесты — treat all as smoke.
    return _extract_legacy_cases(task, level=level)


def _extract_legacy_cases(task: Task, *, level: LevelFilter) -> list[TestCase]:
    """Parse ``task.extra["tests_code"]`` as a Python literal list of tuples."""
    if not case_matches_filter("smoke", level):
        return []

    tests_code = task.extra.get("tests_code", "").strip()
    if not tests_code:
        return []

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
            inp, expected, desc = entry
        elif len(entry) == 2:
            inp, expected = entry
            desc = "test"
        else:
            continue

        if isinstance(inp, tuple):
            args = inp
        else:
            args = (inp,)

        cases.append(
            TestCase(
                args=args,
                kwargs={},
                expected_repr=_safe_repr(expected),
                description=str(desc),
                level="smoke",
            )
        )
    return cases


def _safe_repr(value: Any) -> str:
    """Compute repr of a value. Value comes from mentor tests / our code."""
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
        f"[{icon}] Задача {result.task_id} (v{result.version}): {result.status.upper()} [{result.level}]",
        f"   Пройдено тестов: {result.passed_tests}/{result.total_tests}",
    ]
    for tr in result.results:
        if tr.passed:
            lines.append(f"   + [{tr.level}] {tr.description}")
        else:
            lines.append(f"   x [{tr.level}] {tr.description}")
            lines.append(f"     Ожидалось: {tr.expected_repr}")
            if tr.actual_repr is not None:
                lines.append(f"     Получилось: {tr.actual_repr}")
            if tr.error:
                err_short = tr.error.split("\n")[0][:200]
                lines.append(f"     Ошибка: {err_short}")
    return "\n".join(lines)
