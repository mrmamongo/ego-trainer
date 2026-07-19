"""Progress persistence (.ego/progress.json)."""

from __future__ import annotations

from pathlib import Path

from ego.models import Progress


PROGRESS_PATH = Path(".ego/progress.json")


def load_progress(path: Path = PROGRESS_PATH) -> Progress:
    """Load progress from .ego/progress.json. Returns empty Progress if not found."""
    if not path.exists():
        return Progress()
    return Progress.model_validate_json(path.read_text(encoding="utf-8"))


def save_progress(progress: Progress, path: Path = PROGRESS_PATH) -> None:
    """Save progress to .ego/progress.json. Creates parent dirs if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(progress.model_dump_json(indent=2), encoding="utf-8")
