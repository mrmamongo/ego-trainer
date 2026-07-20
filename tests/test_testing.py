"""Tests for ego.testing — @case / @before / @after + levels."""

from __future__ import annotations

import pytest

from ego.testing import (
    CaseResult,
    TestCase,
    after,
    before,
    case,
    case_matches_filter,
)


def test_case_attaches_list_to_function():
    @case(args=(1,), expected=2, description="inc")
    def task_x(n):
        return n + 1

    assert hasattr(task_x, "_ego_cases")
    assert len(task_x._ego_cases) == 1
    tc = task_x._ego_cases[0]
    assert isinstance(tc, TestCase)
    assert tc.args == (1,)
    assert tc.expected == 2
    assert tc.description == "inc"
    assert tc.level == "smoke"  # default


def test_case_stackable_preserves_source_order():
    @case(args=(0,), expected=0, description="zero", level="smoke")
    @case(args=(-1,), expected=-2, description="neg", level="full")
    def task_x(n):
        return n * 2

    # Top decorator in source = first in _ego_cases (run order).
    assert [c.description for c in task_x._ego_cases] == ["zero", "neg"]
    assert [c.level for c in task_x._ego_cases] == ["smoke", "full"]


def test_case_rejects_invalid_level():
    with pytest.raises(ValueError, match="invalid test level"):

        @case(args=(), expected=None, level="bogus")  # type: ignore[arg-type]
        def task_x():
            pass


def test_before_marks_flag():
    @before
    def setup(task_func):
        return {"ok": True}

    assert setup._ego_before is True
    assert setup(lambda: None) == {"ok": True}


def test_after_marks_flag():
    @after
    def teardown(task_func, case_result, ctx):
        return None

    assert teardown._ego_after is True


def test_case_result_fields():
    cr = CaseResult(
        description="x",
        passed=True,
        expected_repr="1",
        actual_repr="1",
        level="full",
    )
    assert cr.error is None
    assert cr.level == "full"


def test_case_matches_filter():
    assert case_matches_filter("smoke", "smoke")
    assert not case_matches_filter("full", "smoke")
    assert case_matches_filter("full", "full")
    assert not case_matches_filter("smoke", "full")
    assert case_matches_filter("smoke", "all")
    assert case_matches_filter("full", "all")
