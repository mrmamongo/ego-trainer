"""Checker — compares student's solution to reference, runs test cases.

Cases from (in order):
  1. ``Task.tests_file`` (``.tests.py`` with ``@case`` / ``@program`` / hooks)
     — preferred
  2. Legacy ``Task.extra["tests_code"]`` (``ast.literal_eval``, level=smoke)

Level filter (``smoke`` | ``full`` | ``all``, default ``smoke``):
  see docs/TESTS_DESIGN.md. Hypothesis / property — epic 9u7 (full corpus).

Multi-file challenges (ADR-0018 D18.2): :func:`run_stage_check` runs stages
1..N of a challenge folder against one project (``{path: source}``), each
result tagged with its stage; static ``@rules`` see the whole project.

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
from ego.runner import (
    check_project_path,
    include_matches,
    parse_return_value,
    project_view,
    run_function,
    run_project,
    validate_project_files,
    workspace_config,
)
from ego.static_rules import RULE_PREFIX
from ego.static_rules import Rules as StaticRules
from ego.static_rules import evaluate as evaluate_rules
from ego.static_rules import format_violation
from ego.testing import (
    CaseResult,
    LevelFilter,
    ProgramCase,
    TestCase as EgoTestCase,
    TestLevel,
    case_matches_filter,
)
from ego.value_checks import _ego_same_value


@dataclasses.dataclass
class TestCase:
    """Runtime test case used by ``run_check``."""

    __test__ = False  # not a pytest test class

    args: tuple
    kwargs: dict
    expected_repr: str
    description: str
    level: TestLevel = "smoke"
    comparison: str = "repr"
    check_inputs_unchanged: bool = False
    check_result_isolated: bool = False
    input_aliases: tuple = ()
    hide_expected: bool = False
    # Multi-file project: "module.func" instead of the single-file task_*.
    target: str | None = None


@dataclasses.dataclass
class ProgramTest:
    """Runtime ``@program`` case used by :func:`run_stage_check`."""

    __test__ = False  # not a pytest test class

    program: ProgramCase
    # File path of the stage's ``.tests.py`` (shown in the «Файл» hint).
    tests_name: str = ""


HIDDEN_EXPECTED = "<скрыто>"


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
    # 1-based challenge stage; None for ordinary single-file tasks.
    stage: int | None = None
    stage_title: str = ""


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

    @property
    def failed_stages(self) -> list[int]:
        """Stages with at least one failing result (empty = no regression).

        Rule results without a stage (a file of the last stage only) do not
        name a stage.
        """
        return sorted({tr.stage for tr in self.results if not tr.passed and tr.stage is not None})


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
    if not func_name:  # skips _load_tests_module: empty results as before
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

    loaded = _load_tests_module(task, entry_point=func_name)
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

    # Static @rules first: the student sees rule violations and case results.
    rule_results = _static_rule_results(loaded, student_code, entry_point=func_name)
    results.extend(rule_results)

    for tc in test_cases:
        tr = _run_single_case(
            tc,
            task_func=task_func,
            student_code=student_code,
            timeout=timeout,
            before_hook=before_hook,
            after_hook=after_hook,
        )
        if tr.passed:
            passed_count += 1
        elif tr.error == "TIMEOUT":
            had_timeout = True
        elif tr.error is not None:
            had_error = True
        results.append(tr)

    return CheckResult(
        task_id=task.id,
        version=task.version,
        passed_tests=passed_count,
        total_tests=len(results),
        status=_status(results, passed_count, had_timeout, had_error),
        results=results,
        student_code=student_code,
        solution_hash=_hash_code(student_code),
        level=level,
    )


# === Single-file case execution ===


def _run_single_case(
    tc: TestCase,
    *,
    task_func: Callable,
    student_code: str,
    timeout: float,
    before_hook: Callable | None,
    after_hook: Callable | None,
    files: dict[str, str] | None = None,
    workspace: dict | None = None,
) -> TestResult:
    """One ``@case``: before → run → compare → after (see docs/TESTS_DESIGN.md).

    ``files``/``workspace`` are set in a challenge: the case's ``target``
    then runs against the student's project instead of one file's source.
    """
    # Trace exercises must not leak the answer through a failed result.
    shown_expected = HIDDEN_EXPECTED if tc.hide_expected else tc.expected_repr
    ctx: dict = {}
    if before_hook is not None:
        try:
            ctx_raw = before_hook(task_func)
            ctx = ctx_raw if isinstance(ctx_raw, dict) else {}
        except Exception as exc:  # noqa: BLE001
            return TestResult(
                description=tc.description,
                passed=False,
                expected_repr=shown_expected,
                actual_repr=None,
                error=f"@before failed: {exc}",
                level=tc.level,
            )

    run = _execute_case(
        tc,
        task_func=task_func,
        student_code=student_code,
        timeout=timeout,
        files=files,
        workspace=workspace,
    )
    tr = _result_from_run(
        run,
        description=tc.description,
        expected_repr=shown_expected,
        expected_value=tc,
        level=tc.level,
    )
    _call_after(after_hook, task_func, tr, ctx)
    return tr


def _execute_case(
    tc: TestCase,
    *,
    task_func: Callable,
    student_code: str,
    timeout: float,
    files: dict[str, str] | None = None,
    workspace: dict | None = None,
) -> Any:
    """Run one case against single-file or project code (same observations)."""
    if tc.target is not None:
        return run_project(
            files or {},
            target=tc.target,
            args=tc.args,
            kwargs=tc.kwargs,
            workspace=workspace,
            timeout=timeout,
            check_inputs_unchanged=tc.check_inputs_unchanged,
            check_result_isolated=tc.check_result_isolated,
            input_aliases=tc.input_aliases,
        )
    return run_function(
        student_code,
        task_func.__name__,
        args=tc.args,
        kwargs=tc.kwargs,
        timeout=timeout,
        check_inputs_unchanged=tc.check_inputs_unchanged,
        check_result_isolated=tc.check_result_isolated,
        input_aliases=tc.input_aliases,
    )


def _result_from_run(
    run: Any,
    *,
    description: str,
    expected_repr: str,
    expected_value: TestCase,
    level: TestLevel,
) -> TestResult:
    """Turn a :class:`~ego.runner.RunResult` into a :class:`TestResult`."""
    if run.timed_out:
        return TestResult(
            description=description,
            passed=False,
            expected_repr=expected_repr,
            actual_repr=None,
            error="TIMEOUT",
            level=level,
        )
    if run.exception or run.returncode != 0:
        err_lines = run.stderr.splitlines()
        err_msg = "\n".join(err_lines[:10]) if err_lines else "unknown error"
        return TestResult(
            description=description,
            passed=False,
            expected_repr=expected_repr,
            actual_repr=None,
            error=err_msg,
            level=level,
        )
    actual_repr = parse_return_value(run.stdout)
    if actual_repr is None:
        return TestResult(
            description=description,
            passed=False,
            expected_repr=expected_repr,
            actual_repr=None,
            error="no return value (function returned None?)",
            level=level,
        )
    return TestResult(
        description=description,
        passed=_case_passed(actual_repr, expected_value),
        expected_repr=expected_repr,
        actual_repr=actual_repr,
        level=level,
    )


def _case_passed(actual_repr: str, tc: TestCase) -> bool:
    """``repr`` equality, or literal-value equality for ``comparison="value"``."""
    if actual_repr == tc.expected_repr:
        return True
    if tc.comparison != "value":
        return False
    try:
        return _ego_same_value(
            ast.literal_eval(actual_repr), ast.literal_eval(tc.expected_repr)
        )
    except (ValueError, SyntaxError, TypeError, RecursionError):
        return False


def _status(
    results: list[TestResult], passed_count: int, had_timeout: bool, had_error: bool
) -> str:
    """Aggregate status shared by single-file and staged checks."""
    total = len(results)
    has_rule_results = any(_is_rule_result(tr) for tr in results)
    if had_timeout and passed_count == 0:
        return "timeout"
    if had_error and passed_count == 0:
        return "error"
    if passed_count == total and total > 0 and not has_rule_results:
        return "passed"
    if passed_count == 0:
        return "failed"
    return "partial"


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


def _is_rule_result(result: TestResult) -> bool:
    """True for a static-rule result (no expected/actual values to show)."""
    return result.description.startswith(RULE_PREFIX)


def _violation_results(
    rules: StaticRules,
    violations: list,
    *,
    file: str = "",
) -> list[TestResult]:
    """One failing result per violation; ``file`` prefixes project results."""
    results = []
    for violation in violations:
        description = format_violation(violation, rules.message_for(violation))
        if file:
            description = f"{RULE_PREFIX}`{file}`: {description[len(RULE_PREFIX):]}"
        results.append(
            TestResult(
                description=description,
                passed=False,
                expected_repr=violation.trigger,
                actual_repr=None,
                error=None,
                level="smoke",
            )
        )
    return results


def _static_rule_results(
    loaded: _LoadedTests | None,
    student_code: str,
    *,
    entry_point: str,
) -> list[TestResult]:
    """Evaluate ``@rules`` on the student's AST; one failing result per rule.

    A ``SyntaxError`` keeps today's behaviour (the runner reports it per case),
    so parsing failures yield no rule results. ``entry_point`` (the ``task_*``
    function from the reference) satisfies ``require_functions``.
    """
    if loaded is None or loaded.rules is None or loaded.rules.is_empty:
        return []
    try:
        violations = evaluate_rules(student_code, loaded.rules, skip_functions=(entry_point,))
    except SyntaxError:
        return []
    return _violation_results(loaded.rules, violations)


#: ``@rules(file="storage.py")`` — project rules for one file.
_FILE_RULES_ATTR = "_ego_rules_files"


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
    rules: StaticRules | None = None
    # Functions carrying a rules declaration, in module order: (name, rules).
    declared_rules: list[tuple[str, StaticRules]] = dataclasses.field(default_factory=list)
    # Path of the imported .tests.py (None for legacy tests_code).
    tests_file: Path | None = None


def _load_tests_module(task: Task, *, entry_point: str | None = None) -> _LoadedTests | None:
    """Import ``task.tests_file`` via importlib; return None if absent.

    With ``entry_point`` (the solution's ``task_*`` function), ``@rules`` are
    taken from that function only; without it the module-wide first one wins.
    """
    path = task.tests_file
    if path is None or not Path(path).is_file():
        return None
    return load_tests_file(Path(path), entry_point=entry_point)


def load_tests_file(path: Path, *, entry_point: str | None = None) -> _LoadedTests | None:
    """Import one ``.tests.py`` file; ``None`` when it cannot be loaded."""
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
    task_rules: StaticRules | None = None
    declared: list[tuple[str, StaticRules]] = []

    for name in dir(module):
        obj = getattr(module, name)
        if callable(obj) and getattr(obj, "_ego_before", False):
            before_hook = obj
        if callable(obj) and getattr(obj, "_ego_after", False):
            after_hook = obj
        if callable(obj) and name.startswith("task_") and hasattr(obj, "_ego_cases"):
            cases.extend(obj._ego_cases)
        declared_rules = getattr(obj, "_ego_rules", None)
        if callable(obj) and isinstance(declared_rules, StaticRules):
            declared.append((name, declared_rules))
        if not callable(obj) or not isinstance(declared_rules, StaticRules):
            continue
        if entry_point is not None:
            if name == entry_point:
                task_rules = declared_rules
        elif task_rules is None:
            task_rules = declared_rules

    return _LoadedTests(
        module=module,
        cases=cases,
        before_hook=before_hook,
        after_hook=after_hook,
        rules=task_rules,
        declared_rules=declared,
        tests_file=path,
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
            out.append(_to_runtime_case(ec))
        return out

    # Legacy ## Тесты — treat all as smoke.
    return _extract_legacy_cases(task, level=level)


def _to_runtime_case(ec: EgoTestCase) -> TestCase:
    """``ego.testing.TestCase`` (mentor declaration) → checker's runtime case."""
    return TestCase(
        args=ec.args if isinstance(ec.args, tuple) else (ec.args,),
        kwargs={},
        expected_repr=_safe_repr(ec.expected),
        description=ec.description or "test",
        level=ec.level,
        comparison=ec.comparison,
        check_inputs_unchanged=ec.check_inputs_unchanged,
        check_result_isolated=ec.check_result_isolated,
        input_aliases=ec.input_aliases,
        hide_expected=ec.hide_expected,
        target=ec.target,
    )


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


def hash_project(files: dict[str, str]) -> str:
    """sha256 over ``{path: content}`` — the project's submission hash."""
    return _hash_code(project_view(files))


# === Multi-file challenges (ADR-0018) ===


@dataclasses.dataclass
class StageTests:
    """One challenge stage for :func:`run_stage_check`.

    ``task`` is the parsed stage ``.md`` (id/title/version/tests_file);
    ``number`` is its 1-based position in the challenge.
    """

    __test__ = False  # not a pytest test class

    task: Task
    number: int
    title: str = ""


def run_stage_check(
    stage_task: Task,
    files: dict[str, str],
    *,
    stages: list[StageTests],
    timeout: float = 5.0,
    level: LevelFilter = "smoke",
    workspace: dict | None = None,
) -> CheckResult:
    """Check stage N of a challenge: run the tests of stages 1..N (D18.2).

    Regression as in CodeCrafters — a broken stage 2 fails stage 5. The
    project ``files`` (``{path: source}``) are validated against ``workspace``
    first (``ValueError`` with Russian messages; the server turns it into a
    422). ``stages`` lists the challenge's stages in order; only those up to
    ``stage_task`` run.

    Every result carries ``stage`` — the stage whose tests it comes from, so
    a regression names the broken stage. Rule violations are tagged
    «Этап K · …»: in a project you see the rules of every stage at once.
    ``status``/``passed_tests``/``total_tests`` describe the whole run (1..N):
    the server writes progress for stage N only, from that.
    """
    if level not in ("smoke", "full", "all"):
        raise ValueError(f"invalid level filter: {level!r}")
    position = next(
        (index for index, stage in enumerate(stages) if stage.task.id == stage_task.id),
        None,
    )
    errors = validate_project_files(files, workspace)
    if position is None:
        errors.append(f"этап `{stage_task.id}` не найден среди этапов челленджа")
    if errors:
        raise ValueError("; ".join(errors))

    results: list[TestResult] = []
    passed_count = 0
    had_timeout = False
    had_error = False
    for stage in stages[: position + 1]:
        stage_results = [
            *_project_rule_results(stage, files, workspace),
            *_stage_case_results(stage, files, level=level, timeout=timeout, workspace=workspace),
        ]
        for tr in stage_results:
            if tr.passed:
                passed_count += 1
            elif tr.error == "TIMEOUT":
                had_timeout = True
            elif tr.error is not None:
                had_error = True
        results.extend(stage_results)

    return CheckResult(
        task_id=stage_task.id,
        version=stage_task.version,
        passed_tests=passed_count,
        total_tests=len(results),
        status=_status(results, passed_count, had_timeout, had_error)
        if results
        else "no_tests",
        results=results,
        student_code=project_view(files),
        solution_hash=hash_project(files),
        level=level,
    )


def _stage_case_results(
    stage: StageTests,
    files: dict[str, str],
    *,
    level: LevelFilter,
    timeout: float,
    workspace: dict | None,
) -> list[TestResult]:
    """``@case(target=…)`` and ``@program`` of one stage, tagged with ``stage``."""
    loaded = _load_tests_module(stage.task)
    cases = [
        case
        for case in _extract_test_cases(stage.task, level=level, loaded=loaded)
        if case.target is not None
    ]
    programs = [
        ProgramTest(program=program_case)
        for name in (dir(loaded.module) if loaded is not None else [])
        for obj in (getattr(loaded.module, name),)
        for program_case in (getattr(obj, "_ego_programs", ()) if callable(obj) else ())
        if case_matches_filter(program_case.level, level)
    ]
    if not cases and not programs:
        return []
    before_hook, after_hook = _find_hooks(loaded)
    # Hooks of a challenge receive a stub named after the stage (task id).
    task_func = _make_task_func_stub(stage.task.id)

    out: list[TestResult] = []
    for case in cases:
        out.append(
            _run_single_case(
                case,
                task_func=task_func,
                student_code="",
                timeout=timeout,
                before_hook=before_hook,
                after_hook=after_hook,
                files=files,
                workspace=workspace,
            )
        )
    for item in programs:
        out.append(_run_program(item, files, workspace=workspace, timeout=timeout))
    for tr in out:
        tr.stage = stage.number
        tr.stage_title = stage.title
    return out


def _run_program(
    item: ProgramTest,
    files: dict[str, str],
    *,
    workspace: dict | None,
    timeout: float,
) -> TestResult:
    """One ``@program``: the case's files laid over the project, entry run."""
    program = item.program
    description = program.description or "запуск программы"
    if program.entry:
        description = f"{description} ({program.entry})"
    shown = HIDDEN_EXPECTED if program.hide_expected else program.expected_stdout
    # Extra files of the case (a JSON fixture, a config) are not student code:
    # they skip include/limit checks, bad paths are still rejected.
    extra = {
        path: content
        for path, content in program.files.items()
        if check_project_path(path) is None
    }
    project = {**files, **extra}
    # Data files of a case (``data/store.json``) are not collected by
    # ``include``; with at least one such file the per-file include check is
    # lifted for the run — paths were checked above and the file budget is
    # raised by them, so the student's own limits still apply.
    scope = None
    if set(extra) - set(files):
        spec = workspace_config(workspace)
        spec["include"] = [*spec["include"], *(path for path in extra if path not in files)]
        spec["max_files"] = spec["max_files"] + len(project) - len(files)
        scope = spec
    run = run_project(
        project,
        entry=program.entry,
        stdin=program.stdin,
        expected_stdout=program.expected_stdout,
        match=program.match,
        expected_exit=program.expected_exit,
        expect_files=program.expect_files,
        workspace=scope,
        timeout=program.timeout or timeout,
    )
    if run.timed_out:
        return TestResult(description, False, shown, None, "TIMEOUT", level=program.level)
    if run.exception or run.returncode != 0:
        error = "\n".join(run.stderr.splitlines()[:10]) or "unknown error"
        return TestResult(description, False, shown, None, error, level=program.level)
    return TestResult(description, True, shown, run.stdout, level=program.level)


#: Rules that talk about the whole project (``require_functions``, OOP).
_PROJECT_RULE_KEYS = (
    "require_functions",
    "require_classes",
    "require_decorators",
    "require_methods",
    "require_methods_inherited",
    "require_bases",
    "forbid_bases",
    "forbid_attributes_outside_class",
)


def _project_rule_results(
    stage: StageTests, files: dict[str, str], workspace: dict | None
) -> list[TestResult]:
    """Static ``@rules`` of one stage over the project's ``.py`` files (D18.3).

    Rows are tagged with the stage: «Этап K · Правило: …» (plus the file,
    when a rule is scoped to one file). ``require_functions`` and the OOP
    rules see the whole project as one module; every other rule runs per
    file, so a violation names the file to open. An ``import`` of a module
    that belongs to the project itself is never a violation.
    """
    loaded = _load_tests_module(stage.task)
    if loaded is None or not loaded.declared_rules:
        return []
    include = list(workspace_config(workspace)["include"])
    py_files = {
        path: source
        for path, source in sorted(files.items())
        if path.endswith(".py") and include_matches(path, include)
    }
    if not py_files:
        return []
    own_modules = {_module_name(path) for path in py_files}
    results: list[TestResult] = []
    for name, rules in loaded.declared_rules:
        scoped = getattr(getattr(loaded.module, name, None), _FILE_RULES_ATTR, {})
        if scoped:
            for file, file_rules in scoped.items():
                if file not in py_files:
                    results.append(
                        TestResult(
                            description=f"{RULE_PREFIX}файл `{file}` не найден в проекте",
                            passed=False,
                            expected_repr=file,
                            actual_repr=None,
                            level="smoke",
                        )
                    )
                    continue
                results.extend(_file_rule_results(file_rules, py_files[file], file, own_modules))
            continue
        if rules.is_empty:
            continue
        for path, source in py_files.items():
            results.extend(_file_rule_results(rules, source, path, own_modules))
        results.extend(_project_wide_rule_results(rules, py_files))
    return results


def _file_rule_results(
    rules: StaticRules, source: str, path: str, own_modules: set[str]
) -> list[TestResult]:
    """Per-file rules (``forbid_*``) of one project file; file-prefixed rows."""
    file_rules = _without_project_rules(rules)
    if file_rules.is_empty:
        return []
    try:
        violations = evaluate_rules(source, file_rules)
    except SyntaxError:
        return []  # the runner reports the syntax error per case
    return _violation_results(
        rules,
        [
            violation
            for violation in violations
            if not (violation.rule == "import" and violation.trigger in own_modules)
        ],
        file=path,
    )


def _project_wide_rule_results(rules: StaticRules, py_files: dict[str, str]) -> list[TestResult]:
    """``require_functions`` / OOP rules over the concatenated project sources."""
    project_rules = _only_project_rules(rules)
    if project_rules.is_empty:
        return []
    sources = list(py_files.values())
    if not all(_parses(source) for source in sources):
        return []
    try:
        violations = evaluate_rules("\n".join(sources), project_rules)
    except SyntaxError:
        return []
    return _violation_results(rules, violations)


def _without_project_rules(rules: StaticRules) -> StaticRules:
    """``rules`` with the project-wide keys dropped (per-file evaluation)."""
    values = {
        key: () if isinstance(getattr(rules, key), tuple) else {}
        for key in _PROJECT_RULE_KEYS
    }
    return dataclasses.replace(rules, **values)


def _only_project_rules(rules: StaticRules) -> StaticRules:
    """``rules`` with the per-file ``forbid_*`` keys dropped."""
    return dataclasses.replace(
        rules,
        forbid_names=(),
        forbid_methods=(),
        forbid_imports=(),
        forbid_nodes=(),
    )


def _parses(source: str) -> bool:
    try:
        ast.parse(source)
    except SyntaxError:
        return False
    return True


def _module_name(path: str) -> str:
    """``pkg/store.py`` → ``pkg.store``; ``store.py`` → ``store``."""
    return path[: -len(".py")].replace("/", ".")



def count_smoke_checks(result: CheckResult) -> int:
    """Smoke behaviour checks in a result (``@rules`` rows are not checks).

    Works for a single-file check and for a staged run: a stage check asked
    for the ``smoke`` level only, so every behaviour result is a smoke one.
    """
    return sum(not _is_rule_result(tr) and tr.level == "smoke" for tr in result.results)


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
        elif _is_rule_result(tr):
            # Static @rules result: no expected/actual values to show.
            lines.append(f"   x [{tr.level}] {tr.description}")
        else:
            lines.append(f"   x [{tr.level}] {tr.description}")
            lines.append(f"     Ожидалось: {tr.expected_repr}")
            if tr.actual_repr is not None:
                lines.append(f"     Получилось: {tr.actual_repr}")
            if tr.error:
                err_short = tr.error.split("\n")[0][:200]
                lines.append(f"     Ошибка: {err_short}")
    return "\n".join(lines)
