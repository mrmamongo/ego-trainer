"""ego pull — тянуть задачи с сервера в tasks/ + .ego/cache/sol/.

Flow (per ADR-0001 D4, D5):
  1. Читать .ego/config.yaml → server_url, token
  2. GET /tasks (list) → получить список задач (meta)
  3. Для каждой задачи (по фильтру --block/--task/--all):
     a. GET /tasks/<id> → TaskFull (statement_md, stub_py, solution_py)
     b. Записать tasks/<slug>/task_<id>.md (условие, видимое студенту)
     c. Записать tasks/<slug>/task_<id>.py (stub, для редактирования)
     d. Записать .ego/cache/sol/<id>.py (эталон, скрыт от TUI)
     e. Записать .ego/cache/cond/<id>.md (кэш условия)
  4. Обновить .ego/manifest.yaml (что выгружено, версии, хэши)

See beads ego-trainer-8bv.4.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from ego.models import Manifest, ManifestTaskEntry


def run(args) -> int:
    """Entry point for `ego pull`."""
    ego_dir = Path(".ego")
    if not ego_dir.exists():
        print(".ego/ not found. Run `ego init` first.", file=sys.stderr)
        return 1

    # Load config.
    try:
        from ego.models import Config

        config = Config.model_validate_json(
            (ego_dir / "config.yaml").read_text(encoding="utf-8")
        )
    except Exception as e:  # noqa: BLE001
        print(f"Failed to read .ego/config.yaml: {e}", file=sys.stderr)
        return 1

    if not config.server_url:
        print("No server_url configured. Use `ego init --server-url <url>`.", file=sys.stderr)
        return 1

    if not config.token:
        print("No auth token. Run `ego init` with login (not implemented yet).", file=sys.stderr)
        return 1

    # Make HTTP request to server.
    try:
        import urllib.request
        import urllib.error
    except ImportError:
        print("urllib not available", file=sys.stderr)
        return 1

    headers = {"Authorization": f"Bearer {config.token}"}

    # 1. GET /tasks (list).
    try:
        req = urllib.request.Request(
            f"{config.server_url}/tasks", headers=headers
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            tasks_list = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"Failed to fetch tasks: HTTP {e.code} {e.reason}", file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f"Failed to connect to server: {e.reason}", file=sys.stderr)
        return 1

    # 2. Filter tasks.
    block_filter = getattr(args, "block", None)
    task_filter = getattr(args, "task", None)
    pull_all = getattr(args, "all", False)

    if not pull_all and not block_filter and not task_filter:
        print("Specify --all, --block <letter>, or --task <id>.", file=sys.stderr)
        return 1

    selected = []
    for t in tasks_list:
        if task_filter and t["id"] != task_filter:
            continue
        if block_filter and t["block"] != block_filter:
            continue
        selected.append(t)

    if not selected:
        print("No tasks matched the filter.", file=sys.stderr)
        return 1

    # 3. Pull each task.
    pulled = 0
    errors = 0
    manifest_entries: list[ManifestTaskEntry] = []

    for t_meta in selected:
        task_id = t_meta["id"]
        try:
            # GET /tasks/<id> (full, with solution for cache).
            req = urllib.request.Request(
                f"{config.server_url}/tasks/{task_id}",
                headers=headers,
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                task_full = json.loads(resp.read().decode("utf-8"))

            # Also GET /tasks/<id>/solution (needs mentor/admin, but try).
            solution_py = task_full.get("solution_py", "")
            if not solution_py:
                # Try the solution endpoint.
                try:
                    req2 = urllib.request.Request(
                        f"{config.server_url}/tasks/{task_id}/solution",
                        headers=headers,
                    )
                    with urllib.request.urlopen(req2, timeout=30) as resp2:
                        sol_data = json.loads(resp2.read().decode("utf-8"))
                        solution_py = sol_data.get("solution_py", "")
                except urllib.error.HTTPError:
                    pass  # student can't get solution — that's OK for pull

            # Write files.
            slug = t_meta["slug"]
            normalized = task_id.replace(".", "_").lower()
            filename = f"task_{normalized}"

            # tasks/<slug>/<filename>.md (condition, visible to student).
            tasks_dir = Path("tasks") / slug
            tasks_dir.mkdir(parents=True, exist_ok=True)
            (tasks_dir / f"{filename}.md").write_text(
                task_full["statement_md"], encoding="utf-8"
            )

            # tasks/<slug>/<filename>.py (stub, for editing).
            (tasks_dir / f"{filename}.py").write_text(
                task_full["stub_py"], encoding="utf-8"
            )

            # .ego/cache/sol/<id>.py (reference solution, hidden).
            sol_dir = ego_dir / "cache" / "sol"
            sol_dir.mkdir(parents=True, exist_ok=True)
            (sol_dir / f"{task_id}.py").write_text(
                solution_py or "# Solution not available", encoding="utf-8"
            )

            # .ego/cache/cond/<id>.md (cached condition).
            cond_dir = ego_dir / "cache" / "cond"
            cond_dir.mkdir(parents=True, exist_ok=True)
            (cond_dir / f"{task_id}.md").write_text(
                task_full["statement_md"], encoding="utf-8"
            )

            manifest_entries.append(
                ManifestTaskEntry(
                    id=task_id,
                    block=t_meta["block"],
                    slug=slug,
                    version=t_meta["version"],
                    content_hash=t_meta["content_hash"],
                    pulled_at=datetime.now(timezone.utc),
                    md_path=str(tasks_dir / f"{filename}.md"),
                )
            )
            pulled += 1
            print(f"  + {task_id}: {t_meta['title']} (v{t_meta['version']})")

        except Exception as e:  # noqa: BLE001
            print(f"  x {task_id}: {e}", file=sys.stderr)
            errors += 1

    # 4. Update manifest.
    if manifest_entries:
        manifest = Manifest(
            tasks=manifest_entries,
            server_version="0.1.0",
            last_pull_at=datetime.now(timezone.utc),
        )
        (ego_dir / "manifest.yaml").write_text(
            manifest.model_dump_json(indent=2), encoding="utf-8"
        )

    print(f"\nPulled: {pulled}, Errors: {errors}")
    return 0 if errors == 0 else 1
