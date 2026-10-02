"""Exercise checks through the public parser and subprocess checker APIs."""

from pathlib import Path

import pytest

from ego.checker import run_check
from ego.models import Task
from ego.parser import parse_task_file
from ego.testing import case


def make_task(tmp_path: Path, args: str, expected: str, options: str = "") -> Task:
    tests_path = tmp_path / "task_probe.tests.py"
    tests_path.write_text(
        "from ego.testing import case\n"
        f"@case(args={args}, expected={expected}{options})\n"
        "def task_probe(*args):\n    ...\n",
        encoding="utf-8",
    )
    return Task(
        id="PROBE", block="P", slug="probe", task_id="PROBE", title="Contract probe",
        level="easy", md_path=tmp_path / "task_probe.md", tests_file=tests_path,
        solution_py="def task_probe(*args):\n    pass\n",
        statement_md="Contract probe", stub_py="def task_probe(*args):\n    pass\n",
    )


def test_value_comparison_accepts_reordered_nested_dicts(tmp_path):
    task = make_task(
        tmp_path, "()", "{'a': 1, 'nested': {'x': [True, None], 'y': 2}}",
        ", comparison='value'",
    )
    result = run_check(task, "def task_probe():\n    return {'nested': {'y': 2, 'x': [True, None]}, 'a': 1}\n")
    assert result.all_passed


def test_default_repr_comparison_is_unchanged(tmp_path):
    task = make_task(tmp_path, "()", "{'a': 1, 'b': 2}")
    result = run_check(task, "def task_probe():\n    return {'b': 2, 'a': 1}\n")
    assert not result.all_passed


@pytest.mark.parametrize(
    ("expected", "actual"),
    [
        ("{'x': True}", "{'x': 1}"),
        ("{False: 'x'}", "{0: 'x'}"),
        ("[1, 2]", "[2, 1]"),
        ("[1]", "(1,)"),
    ],
)
def test_value_comparison_preserves_types_and_sequence_order(tmp_path, expected, actual):
    task = make_task(tmp_path, "()", expected, ", comparison='value'")
    assert not run_check(task, f"def task_probe():\n    return {actual}\n").all_passed


@pytest.mark.parametrize("mutation", ["arg['items'].append(3)", "arg['flag'] = 0"])
def test_unchanged_input_check_observes_nested_and_type_changes(tmp_path, mutation):
    task = make_task(
        tmp_path, "({'items': [1, 2], 'flag': False},)", "True",
        ", comparison='value', check_inputs_unchanged=True",
    )
    result = run_check(task, f"def task_probe(arg):\n    {mutation}\n    return True\n")
    assert not result.all_passed
    assert "input arguments were modified" in result.results[0].error


def test_mutation_observation_is_opt_in(tmp_path):
    task = make_task(tmp_path, "([],)", "True")
    assert run_check(task, "def task_probe(arg):\n    arg.append(1)\n    return True\n").all_passed


def test_isolation_check_rejects_returned_input_subtree(tmp_path):
    task = make_task(
        tmp_path, "({'child': [1]},)", "{'value': [1]}",
        ", comparison='value', check_inputs_unchanged=True, check_result_isolated=True",
    )
    result = run_check(task, "def task_probe(arg):\n    return {'value': arg['child']}\n")
    assert not result.all_passed
    assert "result shares mutable data with input" in result.results[0].error
    assert run_check(task, "def task_probe(arg):\n    return {'value': list(arg['child'])}\n").all_passed


def test_shared_preferences_fixture_survives_subprocess_boundary(tmp_path):
    task = make_task(
        tmp_path,
        "({'A': {'preferences': {'language': 'ru'}}, 'B': {'preferences': {'language': 'ru'}}},)",
        "{'A': {'preferences': {'language': 'en'}}, 'B': {'preferences': {'language': 'ru'}}}",
        ", comparison='value', check_inputs_unchanged=True, check_result_isolated=True, "
        "input_aliases=(((0, 'B', 'preferences'), (0, 'A', 'preferences')),)",
    )
    global_copy_only = (
        "from copy import deepcopy\n"
        "def task_probe(profiles):\n"
        "    result = deepcopy(profiles)\n"
        "    result['A']['preferences']['language'] = 'en'\n"
        "    return result\n"
    )
    assert not run_check(task, global_copy_only).all_passed
    detached = global_copy_only.replace(
        "    result['A']['preferences']['language'] = 'en'",
        "    result['A'] = deepcopy(result['A'])\n"
        "    result['A']['preferences']['language'] = 'en'",
    )
    assert run_check(task, detached).all_passed


def test_alias_can_link_entire_positional_arguments(tmp_path):
    task = make_task(
        tmp_path, "([], [])", "True",
        ", comparison='value', input_aliases=(((1,), (0,)),)",
    )
    assert run_check(task, "def task_probe(a, b):\n    return a is b\n").all_passed


def test_case_rejects_unknown_comparison_and_invalid_alias_root():
    with pytest.raises(ValueError, match="invalid comparison"):
        case(args=(), expected=None, comparison="approximate")
    with pytest.raises(ValueError, match="positional argument index"):
        case(args=({},), expected=None, input_aliases=((("root",), (0,)),))


def test_parser_delivers_explicit_bug_starter_and_hashes_changes(tmp_path):
    path = tmp_path / "task_probe.md"
    path.write_text("# Задача PROBE: Debug\n\n## Условие\nFix the bug.\n", encoding="utf-8")
    path.with_suffix(".solution.py").write_text(
        "def task_probe(value):\n    return value + 1\n", encoding="utf-8"
    )
    starter = "def task_probe(value):\n    return value - 1\n"
    path.with_suffix(".student.py").write_text(starter, encoding="utf-8")
    first = parse_task_file(path)
    assert first.stub_py == starter
    path.with_suffix(".student.py").write_text(starter.replace("- 1", "- 2"), encoding="utf-8")
    assert parse_task_file(path).content_hash != first.content_hash


def test_parser_without_sidecar_keeps_generated_stub(tmp_path):
    path = tmp_path / "task_probe.md"
    path.write_text("# Задача PROBE: New\n\n## Условие\nWrite code.\n", encoding="utf-8")
    path.with_suffix(".solution.py").write_text(
        "def task_probe(value):\n    return value + 1\n", encoding="utf-8"
    )
    parsed = parse_task_file(path)
    assert "def task_probe(value)" in parsed.stub_py
    assert "return value + 1" not in parsed.stub_py
