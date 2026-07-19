"""ego-tui CLI — separate entry-point for the TUI.

Per ADR-0001 D13: three CLIs (ego, ego-server, ego-tui).
This is the TUI entry-point. The actual textual app is implemented in
beads task ego-trainer-x4f.1 (TUI skeleton). For now, this CLI provides
useful commands that work without the full TUI:

  start    — launch the TUI (placeholder until x4f.1)
  list     — list tasks (delegates to ego.cli.list_cmd)
  show     — show task statement (renders .md or .ego/cache/cond/)
  --version
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from ego_tui import __version__


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="ego-tui",
        description="Ego TUI — textual interface for practice tasks. See ADR-0001 D13.",
    )
    parser.add_argument("--version", action="version", version=f"ego-tui {__version__}")
    sub = parser.add_subparsers(dest="command")

    # start
    p_start = sub.add_parser("start", help="Launch the textual TUI (placeholder)")
    p_start.add_argument("--task", default=None, help="Open specific task on start")

    # list
    p_list = sub.add_parser("list", help="List tasks and progress")
    p_list.add_argument("--local", action="store_true", help="Scan docs/tasks/ offline")

    # show
    p_show = sub.add_parser("show", help="Show task statement (markdown rendered)")
    p_show.add_argument("task_id", help="Task id, e.g. F1 or 1.5")
    p_show.add_argument(
        "--local", action="store_true", help="Read from docs/tasks/ directly"
    )

    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "start":
        return _cmd_start(args)
    if args.command == "list":
        return _cmd_list(args)
    if args.command == "show":
        return _cmd_show(args)
    parser.print_help()
    return 0


def _cmd_start(args) -> int:
    """Launch the textual TUI app (x4f.1 skeleton)."""
    try:
        from ego_tui.app import run as run_tui

        return run_tui()
    except ImportError:
        print(
            "ego-tui: textual app requires the `tui` extra.\n"
            "Install with: uv pip install -e '.[tui]'\n"
            "Or use:\n"
            "  ego-tui list --local       — to list tasks\n"
            "  ego-tui show <id> --local  — to view a task statement",
            file=sys.stderr,
        )
        return 1


def _cmd_list(args) -> int:
    """Delegate to ego.cli.list_cmd."""
    from ego.cli.list_cmd import run as run_list

    return run_list(args)


def _cmd_show(args) -> int:
    """Show a task statement.

    Looks for the task in:
      1. .ego/cache/cond/<task_id>.md (if not --local, after ego pull)
      2. docs/tasks/<block>/<task>.md (offline / dev mode)

    Renders markdown to terminal (best-effort: rich if available, else plain).
    """
    task_id = args.task_id
    candidates = _find_task_md(task_id, local=args.local)
    if not candidates:
        print(f"Task '{task_id}' not found.", file=sys.stderr)
        print("Searched:", file=sys.stderr)
        print("  .ego/cache/cond/<id>.md", file=sys.stderr)
        print("  docs/tasks/**/<task>.md", file=sys.stderr)
        return 1

    md_path = candidates[0]
    content = md_path.read_text(encoding="utf-8")

    # Render markdown — try rich, fallback to plain.
    try:
        from rich.console import Console
        from rich.markdown import Markdown

        Console().print(Markdown(content))
    except ImportError:
        # Plain text — strip <details> blocks (they're for эталон).
        content_clean = re.sub(r"<details>.*?</details>", "", content, flags=re.DOTALL)
        print(content_clean)

    print(f"\n---\nSource: {md_path}", file=sys.stderr)
    return 0


def _find_task_md(task_id: str, *, local: bool = False) -> list[Path]:
    """Find .md file for a task id.

    Search order:
      1. If not --local: .ego/cache/cond/<task_id>.md
      2. docs/tasks/<block>/<task_filename>.md (scan all blocks)

    task_id can be 'F1', '1.5', 'A', 'H8'. Filename is task_<id_lower>.md
    (task_f1.md, task_1_5.md, task_a.md, task_h8.md).
    """
    candidates: list[Path] = []

    # .ego/cache/cond/<id>.md (only when not --local).
    if not local:
        cache_path = Path(".ego/cache/cond") / f"{task_id}.md"
        if cache_path.exists():
            candidates.append(cache_path)

    # docs/tasks/<block>/task_<id>.md
    docs_dir = Path("docs/tasks")
    if docs_dir.exists():
        normalized = task_id.replace(".", "_").lower()
        target_name = f"task_{normalized}.md"
        for p in docs_dir.rglob(target_name):
            candidates.append(p)

    return candidates


if __name__ == "__main__":
    sys.exit(main())
