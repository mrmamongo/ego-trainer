"""Check the beginner START pack through the real parser and sandbox runner.

Run from the repository with ``python -m scripts.verify_start_catalog``.
"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

from ego.checker import run_check
from ego.content_repo import discover_repo
from ego.parser import parse_task_file

DEFAULT_CATALOG = Path(__file__).resolve().parents[1] / "docs/tasks/START/catalog"
HIDDEN = "<скрыто>"


def task_signature(source: str) -> tuple[str, str]:
    functions = [
        node
        for node in ast.parse(source).body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("task_")
    ]
    if len(functions) != 1:
        raise ValueError(f"expected one task function, found {len(functions)}")
    return functions[0].name, ast.dump(functions[0].args, include_attributes=False)


def verify(catalog_root: Path, timeout: float = 5.0) -> list[dict]:
    catalog = discover_repo(catalog_root)
    assert not catalog.is_legacy
    assert [project.project.id for project in catalog.projects] == ["python-start"]
    folders = {folder.folder.id: folder for folder in catalog.projects[0].folders}
    assert "01_variables" in folders, sorted(folders)
    discovered = folders["01_variables"].tasks
    ids = [item.frontmatter.id for item in discovered]
    assert ids == [f"V{number:02}" for number in range(1, 14)], ids

    rows = []
    for item in discovered:
        task = parse_task_file(item.md_path)
        starter_path = item.md_path.with_suffix(".student.py")
        assert task.stub_py == starter_path.read_text(encoding="utf-8"), task.id
        assert task.tests_file is not None and task.tests_file.is_file(), task.id
        assert task_signature(task.stub_py) == task_signature(task.solution_py), task.id

        reference = run_check(task, task.solution_py, level="all", timeout=timeout)
        assert reference.all_passed, (task.id, reference.status, reference.results)
        starter = run_check(task, task.stub_py, level="all", timeout=timeout)
        assert not starter.all_passed, f"{task.id} starter is already solved"
        assert starter.status not in {"no_tests", "timeout"}, (task.id, starter.status)
        for result in reference.results + starter.results:
            assert result.expected_repr == HIDDEN, (task.id, result.expected_repr)

        row = {
            "id": task.id,
            "reference": f"{reference.passed_tests}/{reference.total_tests}",
            "starter": f"{starter.passed_tests}/{starter.total_tests}",
            "starter_status": starter.status,
        }
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()
    rows = verify(args.catalog, args.timeout)
    print(json.dumps({"tasks": len(rows), "ok": True}))


if __name__ == "__main__":
    main()
