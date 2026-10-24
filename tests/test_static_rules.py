"""Tests for @rules — opt-in static (AST) checks of the student's code."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from ego.checker import RULE_PREFIX, format_check_result, run_check
from ego.models import Task
from ego.static_rules import Rules, build_rules, evaluate, format_violation
from ego.testing import case, rules

# === Helpers ===


def _spec(**kwargs) -> Rules:
    return build_rules(**kwargs)


def _keys(source: str, **kwargs) -> list[str]:
    return [v.key for v in evaluate(textwrap.dedent(source), _spec(**kwargs))]


def _write_task(tmp_path: Path, tests_src: str, **task_kwargs) -> Task:
    tests_file = tmp_path / "task_x.tests.py"
    tests_file.write_text(textwrap.dedent(tests_src), encoding="utf-8")
    defaults = dict(
        id="X1",
        block="X",
        slug="block_x",
        task_id="X1",
        title="Static rules",
        level="easy",
        md_path=tmp_path / "task_x.md",
        statement_md="# X1",
        stub_py="def task_x(n):\n    pass\n",
        solution_py="def task_x(n):\n    return n * 2\n",
        tests_file=tests_file,
    )
    defaults.update(task_kwargs)
    return Task(**defaults)


# === forbid_names ===


def test_forbid_names_catches_call_and_reference():
    assert _keys("x = sorted([3, 1])\n", forbid_names=["sorted"]) == ["name:sorted"]
    assert _keys("f = max\ny = f(1, 2)\n", forbid_names=["max"]) == ["name:max"]


def test_forbid_names_only_flags_listed_names():
    assert _keys("x = min(1, 2)\n", forbid_names=["sorted", "sum"]) == []
    assert _keys("x = sorted([1])\n", forbid_names=["sum"]) == []


def test_forbid_names_catches_bare_name_anywhere():
    assert _keys("def f():\n    return [x for x in given]\n", forbid_names=["given"]) == [
        "name:given"
    ]


# === forbid_methods ===


def test_forbid_methods_catches_attribute_call_same_line():
    src = "def task_x(a):\n    a.sort()\n    return a\n"
    assert _keys(src, forbid_methods=["sort"]) == ["method:sort"]


def test_forbid_methods_same_line_and_non_listed():
    assert _keys("def f(s):\n    return s.replace('a', 'b')\n", forbid_methods=["replace"]) == [
        "method:replace"
    ]
    assert _keys("def f(s):\n    return s.strip()\n", forbid_methods=["replace"]) == []


# === forbid_imports ===


@pytest.mark.parametrize(
    "src",
    [
        "import math\n",
        "import math as m\n",
        "from math import sqrt\n",
        "from math import sqrt as root\n",
        "def f(x):\n    import math\n    return x\n",
    ],
)
def test_forbid_imports_forms(src):
    assert _keys(src, forbid_imports=["math"]) == ["import:math"]


def test_forbid_imports_ignores_other_modules():
    assert _keys("import json\nfrom json import loads\n", forbid_imports=["math"]) == []


# === forbid_nodes ===


def test_forbid_nodes_reports_each_node_class():
    src = """
        def f():
            global g
            h = lambda: 1
            return [i for i in range(3)]
    """
    assert _keys(src, forbid_nodes=["Global", "Lambda", "ListComp"]) == [
        "node:Global",
        "node:Lambda",
        "node:ListComp",
    ]


def test_forbid_nodes_absent():
    assert _keys("def f():\n    return 1\n", forbid_nodes=["Lambda"]) == []


# === require_functions ===


def test_require_functions_present_and_missing():
    assert _keys("def parse_command(s):\n    return s\n", require_functions=["parse_command"]) == []
    keys = _keys("def task_x(s):\n    return s\n", require_functions=["parse_command"])
    assert keys == ["function:parse_command"]


def test_require_functions_needs_top_level_definition():
    src = "def task_x(s):\n    def parse_command():\n        return s\n    return parse_command()\n"
    assert _keys(src, require_functions=["parse_command"]) == ["function:parse_command"]


# === allow_in / given_ exemption ===


def test_allow_in_exempts_named_function():
    src = "def given_helper():\n    return sorted([1])\n"
    assert _keys(src, forbid_names=["sorted"]) == []
    src2 = "def my_helper():\n    return sorted([1])\n"
    assert _keys(src2, forbid_names=["sorted"], allow_in=["my_helper"]) == []
    assert _keys(src2, forbid_names=["sorted"]) == ["name:sorted"]


def test_given_prefix_always_exempt():
    src = """
        def given_sorted(values):
            return sorted(values)

        def task_x(values):
            return given_sorted(values)
    """
    assert _keys(src, forbid_names=["sorted", "sum"]) == []


def test_allow_in_does_not_hide_violations_elsewhere():
    src = """
        def given_a():
            return sorted([1])

        def my_helper():
            return max([1])

        def other():
            return sum([1])
    """
    keys = _keys(src, forbid_names=["sorted", "max", "sum"], allow_in=["my_helper"])
    assert keys == ["name:sum"]


def test_exempt_function_can_be_nested_and_lambda_scopes_are_checked():
    src = """
        def task_x(n):
            def given_double(x):
                return sorted([x, x])
            f = lambda y: max(y)
            return given_double(n), f([1])
    """
    assert _keys(src, forbid_names=["sorted", "max"]) == ["name:max"]


# === line numbers / one result per key ===


def test_first_line_number_per_key():
    src = """
        a = 1
        b = 2
        x = sorted([3, 1])
        y = sorted([5, 4])
    """
    (violation,) = evaluate(textwrap.dedent(src), _spec(forbid_names=["sorted"]))
    assert violation.line == 4  # dedent keeps the leading newline
    assert "строка 4" in violation.description
    assert "строка 5" not in violation.description


def test_description_format():
    (violation,) = evaluate("def f(a):\n    return sorted(a)\n", _spec(forbid_names=["sorted"]))
    assert violation.description == "Правило: нельзя использовать `sorted` (строка 2)"
    assert violation.trigger == "sorted"
    assert violation.rule == "name"
    assert violation.key == "name:sorted"


def test_missing_function_description_has_no_line():
    (violation,) = evaluate(
        "def task_x(a):\n    return a\n", _spec(require_functions=["parse_command"])
    )
    assert violation.description == "Правило: нужна функция `parse_command`"
    assert "строка" not in violation.description


def test_violations_in_declaration_order():
    src = "sum([1])\nmax = 3\n"
    keys = _keys(src, forbid_names=["max", "sum"])
    assert keys == ["name:max", "name:sum"]


# === syntax errors / empty rules ===


def test_syntax_error_raises():
    with pytest.raises(SyntaxError):
        evaluate("def task_x(:\n", _spec(forbid_names=["sorted"]))


def test_empty_rules_skip_parsing():
    assert evaluate("def task_x(:\n", _spec()) == []


# === decorator: validation ===


def test_decorator_validates_unknown_ast_node():
    with pytest.raises(ValueError, match="unknown ast node"):
        rules(forbid_nodes=["Srted"])


def test_decorator_rejects_ast_base_class():
    with pytest.raises(ValueError):
        rules(forbid_nodes=["AST"])


def test_decorator_rejects_string_instead_of_list():
    with pytest.raises(ValueError):
        rules(forbid_names="sorted")


def test_decorator_rejects_unknown_message_key():
    with pytest.raises(ValueError, match="matches no rule"):
        rules(forbid_names=["sorted"], messages={"sort": "нельзя"})


def test_decorator_accepts_prefixed_message_keys():
    """Method / import / node messages may use their prefixed key."""
    spec = _spec(
        forbid_methods=["sort"],
        forbid_imports=["math"],
        forbid_nodes=["Lambda"],
        messages={"method:sort": "a", "import:math": "b", "node:Lambda": "c"},
    )
    # Stored under the bare rule name.
    assert spec.messages == {"sort": "a", "math": "b", "Lambda": "c"}


def test_message_for_prefers_custom_text():
    spec = _spec(
        forbid_names=["sorted"],
        forbid_methods=["sort"],
        messages={"sorted": "Без sorted", "method:sort": "Без sort"},
    )
    violations = evaluate("sorted([3, 1])\n[] .sort()\n", spec)
    assert [format_violation(v, spec.message_for(v)) for v in violations] == [
        "Правило: Без sorted (строка 1)",
        "Правило: Без sort (строка 2)",
    ]


def test_decorator_rejects_second_rules():
    with pytest.raises(ValueError, match="already declared"):

        @rules(forbid_names=["sorted"])
        @rules(forbid_methods=["sort"])
        def task_x(a): ...


def test_rules_and_case_stack_in_either_order():
    @rules(forbid_names=["sorted"])
    @case(args=(1,), expected=2)
    def task_a(n): ...

    @case(args=(1,), expected=2)
    @rules(forbid_names=["sorted"])
    def task_b(n): ...

    for func in (task_a, task_b):
        assert getattr(func, "_ego_rules", None) is not None
        assert len(func._ego_cases) == 1


# === run_check end-to-end ===


MERGE_TESTS = """
    from ego.testing import case, rules

    @rules(
        forbid_names=["sum", "sorted", "max"],
        forbid_methods=["sort"],
        forbid_imports=["math"],
        forbid_nodes=["Global", "Lambda", "ListComp"],
        allow_in=["given_helper"],
        messages={"sorted": "Сортировку нужно написать самому"},
    )
    @case(args=([1, 3], [2]), expected=[1, 2, 3], description="merge", level="smoke")
    @case(args=([], [1]), expected=[1], description="empty + one", level="smoke")
    @case(args=([2], [1]), expected=[1, 2], description="single", level="full")
    def task_x(a, b):
        ...
"""

MERGE_SOLUTION = """
    def task_x(a, b):
        merged = []
        i = j = 0
        while i < len(a) and j < len(b):  # advance
            if a[i] <= b[j]:
                merged.append(a[i])
                i += 1
            else:
                merged.append(b[j])
                j += 1
        return merged + a[i:] + b[j:]
"""


def test_run_check_reference_passes(tmp_path):
    task = _write_task(tmp_path, MERGE_TESTS, solution_py=textwrap.dedent(MERGE_SOLUTION))
    result = run_check(task, task.solution_py, level="all")
    assert result.status == "passed"
    assert result.total_tests == 3
    assert all(not tr.description.startswith(RULE_PREFIX) for tr in result.results)


def test_run_check_rule_violation_first_and_cases_still_run(tmp_path):
    task = _write_task(
        tmp_path,
        MERGE_TESTS.replace('messages={"sorted": "Сортировку нужно написать самому"},', ""),
    )
    student = "def task_x(a, b):\n    return sorted(a + b)\n"
    result = run_check(task, student)
    assert result.status != "passed"
    assert result.passed_tests == 2  # cases only
    assert result.total_tests == 3  # cases + one rule result
    first = result.results[0]
    assert first.description == "Правило: нельзя использовать `sorted` (строка 2)"
    assert first.expected_repr == "sorted"
    assert first.actual_repr is None
    assert first.error is None
    assert first.level == "smoke"
    assert first.passed is False
    assert [tr.passed for tr in result.results[1:]] == [True, True]
    assert result.status == "partial"


def test_run_check_custom_message(tmp_path):
    task = _write_task(
        tmp_path,
        """
        from ego.testing import case, rules

        @rules(forbid_names=["sorted"], messages={"sorted": "Сортировку нужно написать самому"})
        @case(args=([2, 1],), expected=[1, 2])
        def task_x(values):
            ...
        """,
        solution_py="def task_x(values):\n    return list(values)\n",
    )
    student = "def task_x(values):\n    # line 2\n    return sorted(values)\n"
    result = run_check(task, student)
    assert result.results[0].description == "Правило: Сортировку нужно написать самому (строка 3)"


def test_run_check_method_import_node_rules(tmp_path):
    task = _write_task(
        tmp_path,
        """
        from ego.testing import case, rules

        @rules(forbid_methods=["sort"], forbid_imports=["math"], forbid_nodes=["Global"])
        @case(args=([2, 1],), expected=[1, 2])
        def task_x(values):
            ...
        """,
    )
    student = (
        "import math\n"
        "\n"
        "\n"
        "def task_x(values):\n"
        "    global counter\n"
        "    counter = len(values)\n"
        "    values.sort()\n"
        "    return values + [math.floor(0)] * 0\n"
    )
    result = run_check(task, student)
    assert result.total_tests == 4  # 3 rules + 1 case
    descriptions = [tr.description for tr in result.results]
    # One result per rule key, in @rules declaration order, cases after.
    assert descriptions == [
        "Правило: нельзя вызывать `.sort()` (строка 7)",
        "Правило: нельзя импортировать `math` (строка 1)",
        "Правило: нельзя использовать `global` (строка 5)",
        "test",
    ]
    assert [tr.expected_repr for tr in result.results[:3]] == ["sort", "math", "Global"]
    assert result.passed_tests == 1  # the case itself passes
    assert result.total_tests == 4


def test_run_check_require_function_missing(tmp_path):
    task = _write_task(
        tmp_path,
        """
        from ego.testing import case, rules

        @rules(require_functions=["parse_command"])
        @case(args=(2,), expected=4)
        def task_x(n):
            ...
        """,
    )
    result = run_check(task, "def task_x(n):\n    return n * 2\n")
    assert result.status == "partial"  # case passed, rule failed → never "passed"
    assert result.passed_tests == 1
    assert result.total_tests == 2
    assert result.results[0].description == "Правило: нужна функция `parse_command`"


def test_run_check_syntax_error_keeps_previous_behaviour(tmp_path):
    """A SyntaxError yields no rule results: only the per-case runner error."""
    task = _write_task(tmp_path, MERGE_TESTS)
    broken = run_check(task, "def task_x(a, b):\n    return sorted(a + b\n")
    assert broken.status == "error"
    assert broken.passed_tests == 0
    assert broken.total_tests == 2  # cases only — no rule results
    assert all(not tr.description.startswith(RULE_PREFIX) for tr in broken.results)
    assert all(tr.error for tr in broken.results)


def test_run_check_without_rules_unchanged(tmp_path):
    task = _write_task(
        tmp_path,
        """
        from ego.testing import case

        @case(args=([2, 1],), expected=[1, 2])
        def task_x(values):
            ...
        """,
    )
    result = run_check(task, "def task_x(values):\n    return sorted(values)\n")
    assert result.status == "passed"
    assert result.total_tests == 1


def test_run_check_empty_rules_are_noop(tmp_path):
    task = _write_task(
        tmp_path,
        """
        from ego.testing import case, rules

        @rules()
        @case(args=([2, 1],), expected=[1, 2])
        def task_x(values):
            ...
        """,
    )
    result = run_check(task, "def task_x(values):\n    return sorted(values)\n")
    assert result.status == "passed"
    assert result.total_tests == 1


def test_run_check_rules_ignored_for_level_filtered_cases(tmp_path):
    """Rules belong to the task, not to a level: they run for smoke too."""
    task = _write_task(tmp_path, MERGE_TESTS)
    result = run_check(task, "def task_x(a, b):\n    return sorted(a + b)\n", level="smoke")
    assert result.total_tests == 3  # 1 rule + 2 smoke cases
    assert result.passed_tests == 2


def test_format_check_result_shows_rule_line(tmp_path):
    task = _write_task(
        tmp_path,
        """
        from ego.testing import case, rules

        @rules(forbid_names=["sorted"])
        @case(args=([1, 3], [2]), expected=[1, 2, 3], description="merge")
        def task_x(a, b):
            ...
        """,
    )
    result = run_check(task, "def task_x(a, b):\n    return sorted(a + b)\n")
    text = format_check_result(result)
    assert "x [smoke] Правило: нельзя использовать `sorted` (строка 2)" in text
    assert "Ожидалось:" not in text  # rule rows carry no expected/actual values


def test_reference_solution_violates_own_rules(tmp_path):
    """The verifier gate: a reference that breaks its own rules fails."""
    task = _write_task(
        tmp_path,
        MERGE_TESTS,
        solution_py='def task_x(a, b):\n    """merge."""\n    return sorted(a + b)\n',
    )
    reference = run_check(task, task.solution_py, level="all")
    assert not reference.all_passed
    assert reference.status != "passed"
    assert reference.results[0].description.startswith(RULE_PREFIX)
