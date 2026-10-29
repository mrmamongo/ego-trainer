"""Test decorators for task ``.tests.py`` files.

Public API used by mentors when writing sidecar tests next to ``.md``:

- ``@case(args=..., expected=..., description=..., level="smoke"|"full")``
- ``@rules(...)`` opt-in static AST rules checked against the student's code
  (see ``ego.static_rules``); stackable with ``@case`` in any order
- ``@before`` / ``@after`` hooks around each case

See ``docs/TESTS_DESIGN.md``. Hypothesis ``@scenario`` is post-MVP (epic 9u7)
and lands with the full test corpus — not in this module yet.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Literal

import ego.static_rules as _static_rules

TestLevel = Literal["smoke", "full"]
Comparison = Literal["repr", "value"]

# Which levels are included for a given run_check / CLI filter.
LevelFilter = Literal["smoke", "full", "all"]


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
) -> Callable[[Callable], Callable]:
    """Register a test case on a ``task_*`` function.

    Stackable::

        @case(args=(1,), expected=2, description="inc", level="smoke")
        @case(args=(0,), expected=1, level="full")
        def task_x(n):
            ...
    """
    if level not in ("smoke", "full"):
        raise ValueError(f"invalid test level: {level!r} (expected 'smoke' or 'full')")
    if comparison not in ("repr", "value"):
        raise ValueError(f"invalid comparison: {comparison!r}")
    aliases = []
    for target, source in input_aliases:
        for path in (target, source):
            if not path or type(path[0]) is not int or path[0] < 0:
                raise ValueError("input alias paths must start with a positional argument index")
            if any(type(part) not in (int, str) for part in path):
                raise ValueError("input alias path parts must be integers or strings")
        aliases.append((tuple(target), tuple(source)))

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
            ),
        )
        return func

    return decorator


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
    """
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
