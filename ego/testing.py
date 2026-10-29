"""Test decorators for task ``.tests.py`` files.

Public API used by mentors when writing sidecar tests next to ``.md``:

- ``@case(args=..., expected=..., description=..., level="smoke"|"full")``
- ``@case(target="module.func", args=..., expected=...)`` — call a function of
  a student's project (multi-file challenges, ADR-0018 D18.3)
- ``@program(stdin=..., expected_stdout=...)`` — run the project's entry point
  and compare its output, optional files before/after
- ``@rules(...)`` opt-in static AST rules checked against the student's code
  (see ``ego.static_rules``); stackable with ``@case`` in any order
- ``@before`` / ``@after`` hooks around each case

See ``docs/TESTS_DESIGN.md``. Hypothesis ``@scenario`` is post-MVP (epic 9u7)
and lands with the full test corpus — not in this module yet.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Literal

import ego.static_rules as _static_rules

TestLevel = Literal["smoke", "full"]
Comparison = Literal["repr", "value"]
#: How ``@program`` compares stdout (see ``ego.exec_helpers``).
ProgramMatch = Literal["exact", "lines", "contains"]

# Which levels are included for a given run_check / CLI filter.
LevelFilter = Literal["smoke", "full", "all"]

_PROGRAM_MATCHES = ("exact", "lines", "contains")
# "module.func" (dotted module path + one attribute), as used by @case(target=).
_TARGET_RE = re.compile(r"[A-Za-z_]\w*(\.[A-Za-z_]\w*)*\.[A-Za-z_]\w*")


@dataclass
class TestCase:
    """One explicit test case registered via ``@case``."""

    __test__ = False  # not a pytest test class

    args: tuple
    expected: Any
    description: str = ""
    level: TestLevel = "smoke"
    comparison: Comparison = "repr"
    check_inputs_unchanged: bool = False
    check_result_isolated: bool = False
    input_aliases: tuple = ()
    hide_expected: bool = False
    # Multi-file project (ADR-0018): call module.func instead of the task_*
    # function of a single file; None = the classic single-file case.
    target: str | None = None


@dataclass
class ProgramCase:
    """One whole-program test registered via ``@program``."""

    __test__ = False  # not a pytest test class

    stdin: str = ""
    expected_stdout: str = ""
    description: str = ""
    level: TestLevel = "smoke"
    match: ProgramMatch = "lines"
    expected_exit: int | None = None
    # Optional entry point (default: the challenge workspace entry, main.py).
    entry: str | None = None
    files: dict[str, str] = field(default_factory=dict)
    expect_files: dict[str, Any] = field(default_factory=dict)
    timeout: float | None = None
    hide_expected: bool = False


@dataclass
class CaseResult:
    """Outcome of one case (passed to ``@after`` hooks)."""

    description: str
    passed: bool
    expected_repr: str
    actual_repr: str | None
    error: str | None = None
    level: TestLevel = "smoke"


def case(
    *,
    args: tuple,
    expected: Any,
    description: str = "",
    level: TestLevel = "smoke",
    comparison: Comparison = "repr",
    check_inputs_unchanged: bool = False,
    check_result_isolated: bool = False,
    input_aliases: tuple = (),
    hide_expected: bool = False,
    target: str | None = None,
) -> Callable[[Callable], Callable]:
    """Register a test case on a ``task_*`` function.

    Stackable::

        @case(args=(1,), expected=2, description="inc", level="smoke")
        @case(args=(0,), expected=1, level="full")
        def task_x(n):
            ...

    ``target="module.func"`` calls a function of the student's project
    instead of ``task_*`` from one file (multi-file challenges, ADR-0018)::

        @case(target="commands.parse_command", args=("set a 1",), expected=("SET", ["a", "1"]))
        def task_kv_stage_01():
            ...
    """
    if level not in ("smoke", "full"):
        raise ValueError(f"invalid test level: {level!r} (expected 'smoke' or 'full')")
    if comparison not in ("repr", "value"):
        raise ValueError(f"invalid comparison: {comparison!r}")
    if target is not None and (
        not isinstance(target, str) or _TARGET_RE.fullmatch(target) is None
    ):
        raise ValueError(
            f"invalid target: {target!r} (expected 'module.func', e.g. 'commands.parse_command')"
        )
    aliases = []
    # (target_path, source_path) — not ``target``: that is the @case target.
    for target_path, source_path in input_aliases:
        for path in (target_path, source_path):
            if not path or type(path[0]) is not int or path[0] < 0:
                raise ValueError("input alias paths must start with a positional argument index")
            if any(type(part) not in (int, str) for part in path):
                raise ValueError("input alias path parts must be integers or strings")
        aliases.append((tuple(target_path), tuple(source_path)))

    def decorator(func: Callable) -> Callable:
        if not hasattr(func, "_ego_cases"):
            func._ego_cases = []  # type: ignore[attr-defined]
        # insert(0): outermost @case (top of source) ends up first →
        # mentor writes cases top-to-bottom in run order.
        func._ego_cases.insert(  # type: ignore[attr-defined]
            0,
            TestCase(
                args=args,
                expected=expected,
                description=description,
                level=level,
                comparison=comparison,
                check_inputs_unchanged=check_inputs_unchanged,
                check_result_isolated=check_result_isolated,
                input_aliases=tuple(aliases),
                hide_expected=hide_expected,
                # Always a keyword: positional would land on ``target``.
                target=target,
            ),
        )
        return func

    return decorator


def program(
    *,
    stdin: str = "",
    expected_stdout: str = "",
    description: str = "",
    level: TestLevel = "smoke",
    match: ProgramMatch = "lines",
    expected_exit: int | None = None,
    files: dict[str, str] | None = None,
    expect_files: dict[str, Any] | None = None,
    timeout: float | None = None,
    hide_expected: bool = False,
    entry: str | None = None,
) -> Callable[[Callable], Callable]:
    """Register a black-box run of the project's entry point (ADR-0018 D18.3).

    The entry (``main.py`` by default) starts with ``stdin``, and stdout is
    compared per ``match``: ``lines`` (default: the same non-empty lines,
    indentation ignored), ``exact`` (same characters, trailing spaces and the
    final newline not counted) or ``contains``::

        @program(
            stdin="SET a 1\\nGET a\\nEXIT\\n",
            expected_stdout="OK\\n1\\n",
            description="SET, потом GET",
            files={"data/store.json": '{"x": "5"}'},          # files before the run
            expect_files={"data/store.json": {"x": "5", "a": "1"}},  # JSON after
        )
        def task_kv_stage_04():
            ...

    Arguments are validated at decoration time (``ValueError``): a wrong
    ``level`` / ``match``, non-string ``stdin`` / ``expected_stdout``, a
    non-dict ``files`` / ``expect_files``, a non-integer ``expected_exit`` or
    a non-positive ``timeout``.
    """
    if level not in ("smoke", "full"):
        raise ValueError(f"invalid test level: {level!r} (expected 'smoke' or 'full')")
    if match not in _PROGRAM_MATCHES:
        raise ValueError(f"invalid match: {match!r} (expected one of {', '.join(_PROGRAM_MATCHES)})")
    if not isinstance(stdin, str):
        raise ValueError(f"@program stdin must be a string, got {type(stdin).__name__}")
    if not isinstance(expected_stdout, str):
        raise ValueError(
            f"@program expected_stdout must be a string, got {type(expected_stdout).__name__}"
        )
    if expected_exit is not None and (
        not isinstance(expected_exit, int) or isinstance(expected_exit, bool)
    ):
        raise ValueError(f"@program expected_exit must be an integer code, got {expected_exit!r}")
    if timeout is not None and (not isinstance(timeout, (int, float)) or timeout <= 0):
        raise ValueError(f"@program timeout must be a positive number, got {timeout!r}")
    if entry is not None and (not isinstance(entry, str) or not entry):
        raise ValueError(f"@program entry must be a file name such as 'main.py', got {entry!r}")
    checked_files = _program_files("files", files, strings_only=True)
    checked_expected = _program_files("expect_files", expect_files, strings_only=False)

    def decorator(func: Callable) -> Callable:
        if not hasattr(func, "_ego_programs"):
            func._ego_programs = []  # type: ignore[attr-defined]
        # insert(0) like @case: the outermost decorator runs first.
        func._ego_programs.insert(  # type: ignore[attr-defined]
            0,
            ProgramCase(
                stdin=stdin,
                expected_stdout=expected_stdout,
                description=description,
                level=level,
                match=match,
                expected_exit=expected_exit,
                entry=entry,
                files=dict(checked_files),
                expect_files=dict(checked_expected),
                timeout=timeout,
                hide_expected=hide_expected,
            ),
        )
        return func

    return decorator


def _program_files(name: str, value: dict | None, *, strings_only: bool) -> dict:
    """Validate a ``{path: ...}`` mapping declared on ``@program``."""
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"@program {name} must be a dict {{path: ...}}")
    for path, content in value.items():
        if not isinstance(path, str) or not path:
            raise ValueError(f"@program {name}: paths must be non-empty strings, got {path!r}")
        if strings_only and not isinstance(content, str):
            raise ValueError(f"@program {name}[{path!r}] must be a string (file content)")
    return dict(value)


def rules(
    *,
    forbid_names: list[str] | tuple[str, ...] = (),
    forbid_methods: list[str] | tuple[str, ...] = (),
    forbid_imports: list[str] | tuple[str, ...] = (),
    forbid_nodes: list[str] | tuple[str, ...] = (),
    require_functions: list[str] | tuple[str, ...] = (),
    allow_in: list[str] | tuple[str, ...] = (),
    require_classes: list[str] | tuple[str, ...] = (),
    require_decorators: dict[str, list[str] | tuple[str, ...]] | None = None,
    require_methods: dict[str, list[str] | tuple[str, ...]] | None = None,
    require_methods_inherited: dict[str, list[str] | tuple[str, ...]] | None = None,
    require_bases: dict[str, list[str] | tuple[str, ...]] | None = None,
    forbid_bases: dict[str, list[str] | tuple[str, ...]] | None = None,
    forbid_attributes_outside_class: list[str] | tuple[str, ...] = (),
    messages: dict[str, str] | None = None,
    file: str | None = None,
) -> Callable[[Callable], Callable]:
    """Declare static rules for the task's student code (opt-in, AST-based).

    Stackable with ``@case`` in any order; at most one ``@rules`` per task
    (a second one raises ``ValueError`` at decoration time)::

        @rules(
            forbid_names=["sorted"],
            messages={"sorted": "Сортировку нужно написать самому"},
        )
        @case(args=([3, 1], [2]), expected=[1, 2, 3])
        def task_li21_merge_sorted(a, b):
            ...

    OOP rules (a class may be named by ``"Account"`` and a method by
    ``"Account.balance"``)::

        @rules(
            require_classes=["Account"],
            require_decorators={"Account": ["dataclass"], "Account.balance": ["property"]},
            require_methods={"Account": ["deposit", "__repr__"]},
            require_bases={"Circle": ["Shape"]},
            forbid_bases={"Inventory": ["list", "dict"]},
            forbid_attributes_outside_class=["_balance"],
        )
        def task_oop_account():
            ...

    Functions and classes whose name starts with ``given_`` / ``Given``
    (GIVEN helpers from starters) are always exempt; ``allow_in`` adds more
    exempt function names. Unknown ast node class names (and unknown
    decorators) raise ``ValueError`` here.

    In a multi-file challenge the rules see the whole project's ``.py``
    files (ADR-0018 D18.3); ``file="storage.py"`` limits this declaration to
    one file of the project.
    """
    if file is not None and (not isinstance(file, str) or not file.strip()):
        raise ValueError(f"@rules file must be a project file name, got {file!r}")
    spec = _static_rules.build_rules(
        forbid_names=forbid_names,
        forbid_methods=forbid_methods,
        forbid_imports=forbid_imports,
        forbid_nodes=forbid_nodes,
        require_functions=require_functions,
        allow_in=allow_in,
        require_classes=require_classes,
        require_decorators=require_decorators,
        require_methods=require_methods,
        require_methods_inherited=require_methods_inherited,
        require_bases=require_bases,
        forbid_bases=forbid_bases,
        forbid_attributes_outside_class=forbid_attributes_outside_class,
        messages=messages,
    )

    def decorator(func: Callable) -> Callable:
        if getattr(func, "_ego_rules", None) is not None:
            raise ValueError(
                f"@rules already declared on {getattr(func, '__name__', func)!r}; "
                "put all rule keys in a single @rules(...)"
            )
        func._ego_rules = spec  # type: ignore[attr-defined]
        if file is not None:
            # Project-scoped rules: {project file: rules}; see ego.checker.
            scoped = dict(getattr(func, "_ego_rules_files", {}))
            scoped[file.strip()] = spec
            func._ego_rules_files = scoped  # type: ignore[attr-defined]
        return func

    return decorator


def before(func: Callable) -> Callable:
    """Mark ``func`` as a before-hook. Must return a ``dict`` context."""
    func._ego_before = True  # type: ignore[attr-defined]
    return func


def after(func: Callable) -> Callable:
    """Mark ``func`` as an after-hook: ``(task_func, case_result, ctx) -> None``."""
    func._ego_after = True  # type: ignore[attr-defined]
    return func


def case_matches_filter(case_level: TestLevel, level_filter: LevelFilter) -> bool:
    """Return True if a case at ``case_level`` should run under ``level_filter``."""
    if level_filter == "all":
        return True
    return case_level == level_filter
