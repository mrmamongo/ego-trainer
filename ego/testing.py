"""Test decorators for task ``.tests.py`` files.

Public API used by mentors when writing sidecar tests next to ``.md``:

- ``@case(args=..., expected=..., description=..., level="smoke"|"full")``
- ``@before`` / ``@after`` hooks around each case

See ``docs/TESTS_DESIGN.md``. Hypothesis ``@scenario`` is post-MVP (epic 9u7)
and lands with the full test corpus — not in this module yet.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Literal

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
            ),
        )
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
