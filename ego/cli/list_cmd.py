"""ego list — show tasks and progress.

Two modes:
- Online (after ``ego pull``): reads ``.ego/manifest.yaml`` (what was pulled)
  and ``.ego/progress.json`` (what is solved) and prints a table
  ``BLOCK | TASK | VERSION | STATUS | ATTEMPTS``.
- Offline / ``--local``: scans ``docs/tasks/*.md`` and lists every available
  task (with its file name) and no progress info (``status=new`` for all).

``rich`` is optional (it only ships with the ``tui`` extra, see pyproject.toml).
When it cannot be imported we fall back to a plain aligned-text table.

The Pydantic models ``Manifest`` / ``Progress`` (task ego-trainer-93h.2) are
imported lazily inside :func:`run` so that the offline ``--local`` path stays
decoupled from the server models and works even before they land / without the
``server`` extra installed (ADR-0001, D6 — offline mode is practically free).
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Type-only import: never executed at runtime, so this module imports
    # cleanly even before ego.models is implemented.
    from ego.models import Manifest, Progress


def run(args) -> int:
    """Entry point for ``ego list``."""
    local = getattr(args, "local", False)
    manifest_path = Path(".ego/manifest.yaml")
    progress_path = Path(".ego/progress.json")

    if not manifest_path.exists():
        # Offline / no .ego/ at all.
        return _list_offline()

    # Online path needs the models. Imported lazily so ``--local`` and the
    # helper functions stay usable without them.
    from ego.models import Manifest, Progress

    manifest = Manifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))

    if not manifest.tasks and not local:
        print(
            "No tasks pulled yet. Use `ego pull` or `ego list --local` to scan docs/tasks/.",
            file=sys.stderr,
        )
        return 1

    if local or not manifest.tasks:
        return _list_offline()

    progress = Progress()
    if progress_path.exists():
        progress = Progress.model_validate_json(progress_path.read_text(encoding="utf-8"))

    return _print_table(manifest, progress)


def _list_offline() -> int:
    """Scan ``docs/tasks/*.md`` and list all available tasks (no progress)."""
    tasks_dir = Path("docs/tasks")
    if not tasks_dir.exists():
        print(f"No docs/tasks/ directory found at {tasks_dir.resolve()}", file=sys.stderr)
        print("Run from project root or use `ego init` + `ego pull`.", file=sys.stderr)
        return 1

    rows: list[tuple[str, str, str, str, str, str]] = []
    for md_path in sorted(tasks_dir.rglob("*.md")):
        # Filename stems look like: task_F1, task_1_5, task_a, task_h8.
        name = md_path.stem
        # block = parent dir name, e.g. 'block_f_simple' -> 'F'.
        block_dir = md_path.parent.name
        block = _block_letter(block_dir)
        task_id = _task_id_from_name(name)
        rows.append((block, task_id, md_path.name, "—", "new", "—"))

    if not rows:
        print(f"No .md files found under {tasks_dir.resolve()}", file=sys.stderr)
        return 1

    _print_rows(rows, columns=["BLOCK", "TASK", "FILE", "VERSION", "STATUS", "ATTEMPTS"])
    print(f"\n{len(rows)} tasks found in docs/tasks/. Use `ego check --local <task>` to test.")
    return 0


def _print_table(manifest: Manifest, progress: Progress) -> int:
    """Print the online table from a manifest + progress.

    ``ManifestTaskEntry`` carries ``id`` (the task id, e.g. ``F1``) but no
    ``task_id``/``title`` — so the online table mirrors the task brief:
    блок / задача / версия / статус / попытки.
    """
    rows: list[tuple[str, str, str, str, str]] = []
    for entry in sorted(manifest.tasks, key=lambda e: (e.block, e.id)):
        pe = progress.find(entry.id, entry.version)
        status = pe.status if pe else "new"
        attempts = str(pe.attempts) if pe else "—"
        rows.append((entry.block, entry.id, entry.version, status, attempts))
    _print_rows(rows, columns=["BLOCK", "TASK", "VERSION", "STATUS", "ATTEMPTS"])
    print(f"\n{len(rows)} tasks pulled.")
    return 0


def _print_rows(rows: list[tuple], columns: list[str]) -> None:
    """Print ``rows`` as a table, using rich if available, else plain text."""
    try:
        from rich.console import Console
        from rich.table import Table

        table = Table()
        for col in columns:
            table.add_column(col)
        for row in rows:
            table.add_row(*[str(c) for c in row])
        Console().print(table)
    except ImportError:
        # Plain-text fallback (rich is only in the `tui` extra).
        widths: list[int] = []
        for i, col in enumerate(columns):
            w = len(str(col))
            for r in rows:
                w = max(w, len(str(r[i])))
            widths.append(w)
        header = "  ".join(str(c).ljust(w) for c, w in zip(columns, widths))
        print(header)
        print("-" * len(header))
        for row in rows:
            print("  ".join(str(c).ljust(w) for c, w in zip(row, widths)))


def _block_letter(block_dir: str) -> str:
    """Derive the block letter from a directory name.

    ``block_f_simple`` -> ``F``, ``block_1_logs`` -> ``1``,
    ``block_a_join`` -> ``A``.
    """
    parts = block_dir.split("_")
    if len(parts) >= 2 and parts[0] == "block":
        return parts[1].upper()
    return block_dir


def _task_id_from_name(name: str) -> str:
    """Derive a task id from a markdown filename stem.

    ``task_F1`` -> ``F1``, ``task_1_5`` -> ``1.5``,
    ``task_a`` -> ``A``, ``task_h8`` -> ``H8``.

    The ``task_`` prefix is stripped, ``_`` is turned into ``.`` (numeric
    sub-tasks like ``1_5`` -> ``1.5``) and the remainder is upper-cased so the
    leading letter is normalised (``f1`` -> ``F1``) while digits are untouched.
    """
    if not name.startswith("task_"):
        return name
    rest = name[len("task_"):]
    rest = rest.replace("_", ".")
    return rest.upper()
