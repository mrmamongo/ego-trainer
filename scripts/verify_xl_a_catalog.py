"""Check the publishable XL-A pack through the real parser and sandbox runner.

Run from the repository with ``python -m scripts.verify_xl_a_catalog``.
An alternate catalog root is useful for verifying the uploaded release image.
"""

from __future__ import annotations

import argparse
import ast
import json
from collections import Counter
from pathlib import Path

from ego.checker import run_check
from ego.content_repo import discover_repo
from ego.parser import parse_task_file
from ego.static_rules import RULE_PREFIX

HIDDEN = "<скрыто>"


def is_rule_result(result) -> bool:
    """True for a static ``@rules`` result (see ego.static_rules)."""
    return result.description.startswith(RULE_PREFIX)


def rule_failures(result) -> list[str]:
    """Failing static-rule descriptions — the code breaks its own ``@rules``."""
    return [tr.description for tr in result.results if is_rule_result(tr) and not tr.passed]


def count_cases(result, level: str | None = None) -> int:
    """Behaviour-case count of a check result (static rules excluded)."""
    return sum(
        not is_rule_result(tr) and (level is None or tr.level == level) for tr in result.results
    )


DEFAULT_CATALOG = Path(__file__).resolve().parents[1] / "docs/tasks/XL-A/catalog"


def task_signature(source: str) -> tuple[str, str]:
    functions = [
        node
        for node in ast.parse(source).body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("task_")
    ]
    if len(functions) != 1:
        raise ValueError(f"expected one task function, found {len(functions)}")
    return functions[0].name, ast.dump(functions[0].args, include_attributes=False)


def verify(catalog_root: Path, timeout: float = 5.0) -> dict:
    catalog = discover_repo(catalog_root)
    assert not catalog.is_legacy
    assert [project.project.id for project in catalog.projects] == ["xl-a"]
    assert [folder.folder.id for folder in catalog.projects[0].folders] == ["xl_a"]
    discovered = sorted(catalog.all_tasks, key=lambda item: item.frontmatter.id)
    assert [item.frontmatter.id for item in discovered] == [
        f"XL-A{number:02}" for number in range(1, 28)
    ]
    kinds = Counter()
    rows = []
    for item in discovered:
        task = parse_task_file(item.md_path)
        starter_path = item.md_path.with_suffix(".student.py")
        assert task.stub_py == starter_path.read_text(encoding="utf-8"), task.id
        assert task.tests_file is not None and task.tests_file.is_file(), task.id
        assert task_signature(task.stub_py) == task_signature(task.solution_py), task.id
        task_kinds = set(item.frontmatter.tags) & {"bug", "modify", "new"}
        assert len(task_kinds) == 1, task.id
        kinds.update(task_kinds)

        reference = run_check(task, task.solution_py, level="all", timeout=timeout)
        if not reference.all_passed:
            failures = [
                {
                    "description": result.description,
                    "expected": result.expected_repr,
                    "actual": result.actual_repr,
                    "error": result.error,
                }
                for result in reference.results
                if not result.passed
            ]
            raise AssertionError(f"{task.id} reference failures: {failures!r}")
        # The reference must obey the task's own static @rules.
        assert not rule_failures(reference), (
            task.id,
            "reference violates @rules",
            rule_failures(reference),
        )
        levels = Counter(result.level for result in reference.results if not is_rule_result(result))
        assert levels["smoke"] >= 3 and levels["full"] >= 1, (task.id, levels)
        for result in reference.results:
            if not is_rule_result(result):
                assert result.expected_repr != HIDDEN, (task.id, result.expected_repr)

        starter = run_check(task, task.stub_py, level="smoke", timeout=timeout)
        starter_cases = [result for result in starter.results if not is_rule_result(result)]
        assert len(starter_cases) == levels["smoke"], task.id
        assert all(result.level == "smoke" for result in starter_cases), task.id
        # The starter's GIVEN helpers must not break the task's own rules
        # (the intentional bug may, e.g. an unfinished function).
        assert not rule_failures(starter), (
            task.id,
            "starter violates @rules",
            rule_failures(starter),
        )
        # This task asks for behavior-preserving decomposition: structure needs
        # mentor review, while tests intentionally accept the original behavior.
        if task.id == "XL-A25":
            assert all(result.passed for result in starter_cases), (
                "XL-A25 baseline must preserve behavior"
            )
        else:
            assert not starter.all_passed, f"{task.id} starter is already solved"
        assert starter.status not in {"no_tests", "timeout"}, (task.id, starter.status)
        row = {
            "id": task.id,
            "reference": count_cases(reference),
            "smoke": levels["smoke"],
            "full": levels["full"],
            "starter_smoke_passed": sum(result.passed for result in starter_cases),
            "rules": count_cases(reference) != reference.total_tests,
        }
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
    assert kinds == {"bug": 9, "modify": 9, "new": 9}, kinds
    return {
        "tasks": len(rows),
        "reference_cases": sum(row["reference"] for row in rows),
        "smoke_cases": sum(row["smoke"] for row in rows),
        "full_cases": sum(row["full"] for row in rows),
        "starter_cases": sum(row["smoke"] for row in rows),
        "manual_refactoring_review": ["XL-A25"],
        "results": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = verify(args.catalog, args.timeout)
    if args.report:
        args.report.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(json.dumps({key: value for key, value in report.items() if key != "results"}))


if __name__ == "__main__":
    main()
