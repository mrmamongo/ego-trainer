"""Check the beginner START pack through the real parser and sandbox runner.

Run from the repository with ``python -m scripts.verify_start_catalog``.
"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

from ego.checker import CheckResult, TestResult, run_check
from ego.content_repo import discover_repo
from ego.parser import parse_task_file
from ego.static_rules import RULE_PREFIX

DEFAULT_CATALOG = Path(__file__).resolve().parents[1] / "docs/tasks/START/catalog"
HIDDEN = "<скрыто>"


def is_rule_result(result: TestResult) -> bool:
    """True for a static ``@rules`` result (see ego.static_rules)."""
    return result.description.startswith(RULE_PREFIX)


def rule_failures(result: CheckResult) -> list[str]:
    """Failing static-rule descriptions — the code breaks its own ``@rules``."""
    return [tr.description for tr in result.results if is_rule_result(tr) and not tr.passed]


def count_case_results(result: CheckResult) -> int:
    """Number of behaviour cases in a check result (static rules excluded)."""
    return sum(not is_rule_result(tr) for tr in result.results)


def task_signature(source: str) -> tuple[str, str]:
    functions = [
        node
        for node in ast.parse(source).body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("task_")
    ]
    if len(functions) != 1:
        raise ValueError(f"expected one task function, found {len(functions)}")
    return functions[0].name, ast.dump(functions[0].args, include_attributes=False)


CHECKPOINT_FOLDERS = {"16_review"}

EXPECTED_IDS = {
    "01_variables": [f"V{n:02}" for n in range(1, 14)],
    "02_functions": [f"FN{n:02}" for n in range(1, 23)],
    "03_loops": [f"L{n:02}" for n in range(1, 25)],
    "04_numbers": [f"N{n:02}" for n in range(1, 9)],
    "05_range_while": [f"R{n:02}" for n in range(1, 23)],
    "06_break_nested": [f"BK{n:02}" for n in range(1, 23)],
    "07_strings": [f"S{n:02}" for n in range(1, 23)],
    "08_lists": [f"LI{n:02}" for n in range(1, 23)],
    "09_functions_deep": [f"FD{n:02}" for n in range(1, 21)],
    "10_projects": [f"MP{n:02}" for n in range(1, 21)],
    "11_project_expenses": [f"PX{n:02}" for n in range(1, 9)],
    "12_tuples_sets": [f"TS{n:02}" for n in range(1, 11)],
    "13_dicts": [f"DI{n:02}" for n in range(1, 27)],
    "14_errors": [f"ER{n:02}" for n in range(1, 19)],
    "15_nested": [f"NS{n:02}" for n in range(1, 15)],
    "16_review": [f"RV{n:02}" for n in range(1, 13)],
}


def verify(
    catalog_root: Path,
    timeout: float = 5.0,
    *,
    project_id: str = "python-start",
    expected_ids: dict[str, list[str]] = EXPECTED_IDS,
    checkpoint_folders: set[str] = CHECKPOINT_FOLDERS,
) -> list[dict]:
    catalog = discover_repo(catalog_root)
    assert not catalog.is_legacy
    assert [project.project.id for project in catalog.projects] == [project_id]
    folders = {folder.folder.id: folder for folder in catalog.projects[0].folders}
    assert sorted(folders) == sorted(expected_ids), sorted(folders)

    lesson_folder = verify_theory(folders, expected_ids, checkpoint_folders)
    folder_rank = {folder_id: rank for rank, folder_id in enumerate(expected_ids)}

    rows = []
    for folder_id, folder_ids in expected_ids.items():
        discovered = folders[folder_id].tasks
        ids = [item.frontmatter.id for item in discovered]
        assert ids == folder_ids, (folder_id, ids)
        for item in discovered:
            theory = item.frontmatter.theory
            assert theory, f"{item.frontmatter.id} has no theory"
            unknown = [t for t in theory if t not in lesson_folder]
            assert not unknown, (item.frontmatter.id, "unknown theory ids", unknown)
            later = [t for t in theory if folder_rank[lesson_folder[t]] > folder_rank[folder_id]]
            assert not later, (item.frontmatter.id, "theory from a later folder", later)
            assert len(set(theory)) == len(theory), (item.frontmatter.id, "repeated theory id")
            rows.append(verify_task(item, timeout))
    return rows


def verify_theory(
    folders, expected_ids: dict[str, list[str]], checkpoint_folders: set[str]
) -> dict[str, str]:
    """Every folder has theory cards; lesson ids are unique. Returns id -> folder id."""
    lesson_folder: dict[str, str] = {}
    for folder_id in expected_ids:
        lessons = folders[folder_id].lessons
        # Checkpoint folders test earlier topics and link earlier cards; they have no cards of their own.
        assert lessons or folder_id in checkpoint_folders, f"{folder_id} has no lesson_*.md"
        for lesson in lessons:
            assert not lesson.error, (lesson.md_path.name, lesson.error)
            assert lesson.frontmatter is not None, lesson.md_path.name
            assert lesson.body_md.strip(), f"{lesson.md_path.name} has an empty body"
            lid = lesson.frontmatter.id
            assert lid not in lesson_folder, ("duplicate lesson id", lid)
            lesson_folder[lid] = folder_id
    print(json.dumps({"lessons": len(lesson_folder)}), flush=True)
    return lesson_folder


def verify_task(item, timeout: float) -> dict:
    task = parse_task_file(item.md_path)
    starter_path = item.md_path.with_suffix(".student.py")
    assert task.stub_py == starter_path.read_text(encoding="utf-8"), task.id
    assert task.tests_file is not None and task.tests_file.is_file(), task.id
    stub_sig, solution_sig = task_signature(task.stub_py), task_signature(task.solution_py)
    # A modification task may change the signature (e.g. add a parameter with a default).
    if "modify" in item.frontmatter.tags:
        assert stub_sig[0] == solution_sig[0], task.id
    else:
        assert stub_sig == solution_sig, task.id

    is_trace = "trace" in item.frontmatter.tags
    reference = run_check(task, task.solution_py, level="all", timeout=timeout)
    assert reference.all_passed, (task.id, reference.status, reference.results)
    # all_passed already fails on rule results (they never pass); name them.
    assert not rule_failures(reference), (
        task.id,
        "reference violates @rules",
        rule_failures(reference),
    )
    starter = run_check(task, task.stub_py, level="all", timeout=timeout)
    assert not starter.all_passed, f"{task.id} starter is already solved"
    assert starter.status not in {"no_tests", "timeout"}, (task.id, starter.status)
    for result in reference.results + starter.results:
        if is_rule_result(result):
            continue  # static @rules rows carry a rule key, not an expected value
        hidden = result.expected_repr == HIDDEN
        if is_trace:
            assert hidden, (task.id, "trace answers must be hidden", result.description)
        else:
            # Whole-program tasks may hide some full scenarios; smoke cases stay visible.
            assert not (hidden and result.level == "smoke"), (task.id, "smoke case hidden", result.description)
    if rule_failures(starter):
        # The GIVEN helpers in the starter must not break the task's own rules.
        raise AssertionError((task.id, "starter violates @rules", rule_failures(starter)))

    if not is_trace:
        smoke = run_check(task, task.stub_py, level="smoke", timeout=timeout)
        assert not smoke.all_passed, f"{task.id} starter passes smoke"
        # Rule results count towards total_tests; compare the case counts.
        smoke_cases = count_case_results(smoke)
        assert smoke_cases >= 3, (task.id, smoke_cases)
        assert count_case_results(reference) > smoke_cases, f"{task.id} has no full cases"

    row = {
        "id": task.id,
        "reference": f"{reference.passed_tests}/{reference.total_tests}",
        "starter": f"{starter.passed_tests}/{starter.total_tests}",
        "rules": count_case_results(reference) != reference.total_tests,
        "starter_status": starter.status,
    }
    print(json.dumps(row, ensure_ascii=False), flush=True)
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()
    rows = verify(args.catalog, args.timeout)
    print(json.dumps({"tasks": len(rows), "ok": True}))


if __name__ == "__main__":
    main()
