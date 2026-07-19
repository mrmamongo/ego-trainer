"""ego check <task> — локальная проверка решения + write progress + runs/.

Flow (per ADR-0001 D5, D6, D9, D12):
  1. Найти .md задачи (через .ego/manifest.yaml или fallback в docs/tasks/)
  2. Найти student code в tasks/<block>/<task>.py
  3. Парсить .md → Task (через ego.parser)
  4. run_check(task, student_code) → CheckResult
  5. Обновить .ego/progress.json (upsert ProgressEntry) — если .ego/ есть
  6. Записать лог в .ego/runs/<task_id>-<timestamp>.json — если .ego/ есть
  7. Напечатать результат

`--local` mode (D6): парсит docs/tasks/ напрямую, не требует .ego/.
Прогресс и логи не пишутся (некуда). Полезно для разработки и тестирования.

See beads ego-trainer-8bv.2 (check) and ego-trainer-8bv.3 (--local).
"""

from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from ego.checker import format_check_result, run_check
from ego.models import ProgressEntry, Run
from ego.parser import parse_task_file
from ego.progress import load_progress, save_progress


def run(args) -> int:
    """Entry point for `ego check <task_id>`."""
    task_id = args.task_id
    local = getattr(args, "local", False)
    ego_dir = Path(".ego")

    if not local and not ego_dir.exists():
        print(
            ".ego/ not found. Run `ego init` first, or use `ego check --local`.",
            file=sys.stderr,
        )
        return 1

    # 1. Find the .md file for this task.
    md_path = _find_task_md(task_id, local=local)
    if md_path is None:
        print(f"Task '{task_id}' not found.", file=sys.stderr)
        print("Searched:", file=sys.stderr)
        if not local:
            print("  .ego/manifest.yaml entries", file=sys.stderr)
        print("  docs/tasks/**/<task>.md", file=sys.stderr)
        return 1

    # 2. Parse the .md → Task.
    try:
        task = parse_task_file(md_path)
    except Exception as e:  # noqa: BLE001
        print(f"Failed to parse {md_path}: {e}", file=sys.stderr)
        return 1

    # 3. Find student code.
    student_path = _find_student_code(task_id, task)
    if student_path is None:
        print(f"Student code not found for task '{task_id}'.", file=sys.stderr)
        print("Expected: tasks/<block>/task_<id>.py", file=sys.stderr)
        print("Use `ego pull` to get the stub, or create the file manually.", file=sys.stderr)
        return 1

    student_code = student_path.read_text(encoding="utf-8")

    # 4. Run the checker.
    timeout = _load_timeout(local=local)
    result = run_check(task, student_code, timeout=timeout)
    as_json = getattr(args, "json", False)

    # 5. Print result (human text, or JSON for tooling / VSCode extension).
    if as_json:
        print(json.dumps(_result_to_json(result), ensure_ascii=False))
    else:
        print(format_check_result(result))

    # 6. Update progress + write run log (only if .ego/ exists).
    if ego_dir.exists():
        _update_progress(task_id, task.version, result)
        run_log = _write_run_log(task_id, task.version, result, student_code)
        if not as_json:
            print(f"\nRun logged: {run_log}", file=sys.stderr)
    elif local and not as_json:
        print("\n(--local mode: progress and run log not saved)", file=sys.stderr)

    # Exit code: 0 if all passed, 1 otherwise.
    return 0 if result.all_passed else 1


def _result_to_json(result) -> dict:
    """Serialize CheckResult to the CheckResponse shape used by ego-server / vscode-ego."""
    return {
        "task_id": result.task_id,
        "version": result.version,
        "status": result.status,
        "passed_tests": result.passed_tests,
        "total_tests": result.total_tests,
        "solution_hash": result.solution_hash,
        "results": [
            {
                "description": r.description,
                "passed": r.passed,
                "expected_repr": r.expected_repr,
                "actual_repr": r.actual_repr,
                "error": r.error,
            }
            for r in result.results
        ],
        "log": format_check_result(result),
    }


def _find_task_md(task_id: str, *, local: bool = False) -> Path | None:
    """Find the .md file for a task id.

    Search order:
      1. .ego/manifest.yaml → entry.md_path (if it exists on disk, not --local)
      2. docs/tasks/<block>/task_<id>.md (dev/offline fallback)
    """
    # 1. Manifest (skip in --local mode).
    if not local:
        manifest_path = Path(".ego/manifest.yaml")
        if manifest_path.exists():
            try:
                from ego.models import Manifest

                manifest = Manifest.model_validate_json(
                    manifest_path.read_text(encoding="utf-8")
                )
                for entry in manifest.tasks:
                    if entry.id == task_id:
                        p = Path(entry.md_path)
                        if p.exists():
                            return p
            except Exception:  # noqa: BLE001
                pass  # fall through to docs/tasks/

    # 2. docs/tasks/ fallback.
    docs_dir = Path("docs/tasks")
    if docs_dir.exists():
        normalized = task_id.replace(".", "_").lower()
        target = f"task_{normalized}.md"
        for p in docs_dir.rglob(target):
            return p

    return None


def _find_student_code(task_id: str, task) -> Path | None:
    """Find the student's .py file.

    Per ADR D5: tasks/<block>/<task>.py
    e.g. tasks/block_f_simple/task_f1.py
    """
    normalized = task_id.replace(".", "_").lower()
    filename = f"task_{normalized}.py"

    # Try tasks/<slug>/task_<id>.py (slug from task).
    candidates = [
        Path("tasks") / task.slug / filename,
        Path("tasks") / task.block.lower() / filename,
    ]
    # Also scan tasks/ recursively.
    tasks_dir = Path("tasks")
    if tasks_dir.exists():
        for p in tasks_dir.rglob(filename):
            candidates.append(p)

    for c in candidates:
        if c.exists():
            return c
    return None


def _load_timeout(*, local: bool = False) -> float:
    """Load sandbox timeout from .ego/config.yaml. Default 5.0 in --local mode."""
    if local and not Path(".ego/config.yaml").exists():
        return 5.0
    try:
        from ego.models import Config

        config = Config.model_validate_json(
            Path(".ego/config.yaml").read_text(encoding="utf-8")
        )
        return config.sandbox_timeout_sec
    except Exception:  # noqa: BLE001
        return 5.0


def _update_progress(task_id: str, version: str, result) -> None:
    """Upsert a ProgressEntry in .ego/progress.json."""
    progress = load_progress()
    existing = progress.find(task_id, version)

    # Map checker status to TaskStatus.
    status_map = {
        "passed": "passed",
        "partial": "partial",
        "failed": "new",  # failed → still "new" (not solved)
        "error": "new",
        "timeout": "new",
        "no_tests": "new",
    }
    task_status = status_map.get(result.status, "new")

    attempts = (existing.attempts if existing else 0) + 1

    entry = ProgressEntry(
        task_id=task_id,
        version=version,
        status=task_status,
        attempts=attempts,
        passed_tests=result.passed_tests,
        total_tests=result.total_tests,
        last_run_at=datetime.now(timezone.utc),
        solution_hash=result.solution_hash,
    )
    progress.upsert(entry)
    save_progress(progress)


def _write_run_log(task_id: str, version: str, result, student_code: str) -> Path:
    """Write a run log to .ego/runs/<task_id>-<timestamp>.json."""
    runs_dir = Path(".ego/runs")
    runs_dir.mkdir(parents=True, exist_ok=True)

    run_id = uuid.uuid4().hex[:12]
    ts = datetime.now(timezone.utc)
    ts_str = ts.strftime("%Y%m%dT%H%M%S")
    # Sanitize task_id for filename (replace . with _).
    safe_id = task_id.replace(".", "_")
    filename = f"{safe_id}-{ts_str}-{run_id}.json"
    path = runs_dir / filename

    # Build log text from checker results.
    log_lines = [format_check_result(result)]
    log_text = "\n".join(log_lines)

    # Map checker status to RunStatus (passed/failed/error/timeout).
    run_status_map = {
        "passed": "passed",
        "partial": "failed",  # partial = not fully passed
        "failed": "failed",
        "error": "error",
        "timeout": "timeout",
        "no_tests": "error",  # no tests = can't evaluate
    }
    run_status = run_status_map.get(result.status, "error")

    run = Run(
        id=run_id,
        task_id=task_id,
        version=version,
        started_at=ts,
        finished_at=ts,
        status=run_status,  # type: ignore[arg-type]
        passed_tests=result.passed_tests,
        total_tests=result.total_tests,
        solution_hash=result.solution_hash,
        log=log_text[:8192],  # truncate to 8KB
        error="",
    )
    path.write_text(run.model_dump_json(indent=2), encoding="utf-8")
    return path
