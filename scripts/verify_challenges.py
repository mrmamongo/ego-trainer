"""Check multi-file challenges through the real parser, runner and checker.

Run from the repository with ``python -m scripts.verify_challenges
--catalog <dir> --timeout 30`` (ADR-0018 D18.7). For every ``kind: challenge``
folder of the catalog:

- stages are numbered 1..N, each has frontmatter and a ``.tests.py``;
- every project (``starter/``, ``solution/``, ``stage_K.solution/``) has
  safe paths and fits the ``workspace`` (``include``, ``max_files``);
- ``solution/`` (required: the reference after the last stage) passes every
  stage;
- ``starter/`` (optional) does not pass stage 1;
- ``stage_K.solution/`` (optional) passes stages 1..K and fails K+1;
- every stage has at least three smoke checks and one full check.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ego.checker import (
    StageTests,
    _is_rule_result,
    count_smoke_checks,
    run_stage_check,
)
from ego.content_repo import discover_repo, read_project_files
from ego.parser import parse_task_file
from ego.runner import check_project_path, validate_project_files

DEFAULT_CATALOG = Path(__file__).resolve().parents[1] / "tests/fixtures/challenges_catalog"
#: A starter may already answer a couple of stage-1 checks (its first task
#: often fixes one function), but it must not pass stage 1 as a whole.
ALLOWED_STARTER_PASSES = 1


def verify_challenge(folder, timeout: float) -> list[dict]:
    """Verify one challenge folder; returns one row per stage."""
    workspace = folder.folder.workspace.model_dump() if folder.folder.workspace else None
    include = (workspace or {}).get("include", ["*.py"])
    folder_id = folder.folder.id
    tasks = sorted(folder.tasks, key=lambda item: item.stage or 0)
    assert tasks, f"{folder_id}: challenge has no stages"
    numbers = [item.stage for item in tasks]
    assert numbers == list(range(1, len(tasks) + 1)), (folder_id, "stages are not 1..N", numbers)
    for item in tasks:
        assert item.frontmatter is not None, (folder_id, item.md_path.name, "no frontmatter")
        assert item.tests_path is not None, (folder_id, item.md_path.name, "no .tests.py")
    stages = [
        StageTests(
            task=parse_task_file(item.md_path),
            number=item.stage or 0,
            title=item.frontmatter.title,
        )
        for item in tasks
    ]

    assert folder.solution is not None, f"{folder_id}: no solution/ project"
    projects = {"solution": read_project_files(folder.solution, include)}
    if folder.starter is not None:
        projects["starter"] = read_project_files(folder.starter, include)
    for item in tasks:
        if item.stage_solution is not None:
            projects[_stage_project_name(item.stage or 0)] = read_project_files(
                item.stage_solution, include
            )
    for name, files in projects.items():
        assert files, (folder_id, name, "empty project")
        bad = [path for path in files if check_project_path(path) is not None]
        assert not bad, (folder_id, name, "unsafe paths", bad)
        errors = validate_project_files(files, workspace)
        assert not errors, (folder_id, name, errors)

    rows = []
    for index, stage in enumerate(stages):
        reference = run_stage_check(
            stage.task, projects["solution"], stages=stages, timeout=timeout
        )
        assert reference.all_passed, (stage.task.id, "solution/ fails", failures(reference))
        smoke = count_smoke_checks(reference)
        assert smoke >= 3, (stage.task.id, "fewer than three smoke checks", smoke)

        row = {
            "challenge": folder_id,
            "stage": stage.number,
            "id": stage.task.id,
            "checks": reference.total_tests,
            "smoke": smoke,
        }
        if "starter" in projects and stage.number == 1:
            starter = run_stage_check(
                stage.task, projects["starter"], stages=stages, timeout=timeout
            )
            assert starter.passed_tests <= ALLOWED_STARTER_PASSES, (
                stage.task.id,
                "starter/ passes stage 1",
                failures(starter),
            )
            row["starter"] = f"{starter.passed_tests}/{starter.total_tests}"
        # Level counts come from the starter when present (the reference
        # passes everything and says nothing about the smoke/full split).
        sample = projects.get("starter", projects["solution"])
        if (
            count_smoke_checks(run_stage_check(stage.task, sample, stages=[stage], timeout=timeout))
            < 3
        ):
            raise AssertionError((stage.task.id, "fewer than three smoke checks"))
        if not _has_full_check(stage, sample, timeout):
            raise AssertionError((stage.task.id, "no full checks"))
        current = _stage_project_name(stage.number)
        if current in projects:
            exact = run_stage_check(stage.task, projects[current], stages=stages, timeout=timeout)
            assert exact.all_passed, (current, "fails its own stage", failures(exact))
            if index + 1 < len(stages):
                following = stages[index + 1]
                later = run_stage_check(
                    following.task, projects[current], stages=stages, timeout=timeout
                )
                assert not later.all_passed, (current, "already passes", following.task.id)
        print(json.dumps(row, ensure_ascii=False), flush=True)
        rows.append(row)
    return rows


def _stage_project_name(number: int) -> str:
    """Directory name of the stage's reference project."""
    return f"stage_{number:02}.solution"


def _has_full_check(stage: StageTests, files: dict[str, str], timeout: float) -> bool:
    """True when the stage has at least one behaviour check at ``full`` level."""
    result = run_stage_check(stage.task, files, stages=[stage], level="full", timeout=timeout)
    return any(tr.level == "full" and not _is_rule_result(tr) for tr in result.results)


def failures(result) -> list[tuple[int | None, str]]:
    """``(stage, description)`` of every failing result."""
    return [(tr.stage, tr.description) for tr in result.results if not tr.passed]


def verify(catalog_root: Path, timeout: float = 30.0) -> list[dict]:
    """Verify every challenge of a catalog; returns one row per stage."""
    catalog = discover_repo(catalog_root)
    assert not catalog.is_legacy, f"{catalog_root}: no catalog.yaml"
    return [
        row for folder in catalog.challenge_folders for row in verify_challenge(folder, timeout)
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()
    rows = verify(args.catalog, args.timeout)
    print(
        json.dumps(
            {
                "challenges": len({row["challenge"] for row in rows}),
                "stages": len(rows),
                "ok": True,
            }
        )
    )


if __name__ == "__main__":
    main()
