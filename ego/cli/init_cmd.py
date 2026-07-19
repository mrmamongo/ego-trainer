"""ego init — create .ego/ in current directory, login or --local."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from ego.models import Config, Manifest, Progress


CWD_EGO = Path(".ego")


def run(args) -> int:
    """Entry point for `ego init`. Returns exit code."""
    if CWD_EGO.exists() and not args.force:
        print(f".ego/ already exists at {CWD_EGO.resolve()}", file=sys.stderr)
        print("Use --force to overwrite.", file=sys.stderr)
        return 1

    if args.local:
        return _init_local(args)
    return _init_online(args)


def _init_local(args) -> int:
    """Offline mode: no server, no auth, just create .ego/ with default config."""
    config = Config(
        server_url="",
        token="",
        student_id="local",
        student_username="local-user",
        role="student",
    )
    _write_egdir(config, Manifest(tasks=[], last_pull_at=None))
    print("Initialized .ego/ in offline (--local) mode.")
    print("Use `ego check --local <task>` to test against docs/tasks/*.md.")
    return 0


def _init_online(args) -> int:
    """Online mode: prompt for server, then login (stub — real auth in 8bv.2)."""
    server_url = args.server_url
    config = Config(server_url=server_url, token="", student_id="", student_username="")
    _write_egdir(config, Manifest(tasks=[], last_pull_at=None))
    print(f"Initialized .ego/ pointing to {server_url}")
    print("Login not implemented yet (see beads ego-trainer-8bv.2).")
    print("For now use `ego init --local` for offline development.")
    return 0


def _write_egdir(config: Config, manifest: Manifest) -> None:
    """Create .ego/ with config.yaml, manifest.yaml, progress.json, dirs."""
    if CWD_EGO.exists():
        # --force: clean and recreate
        shutil.rmtree(CWD_EGO)
    CWD_EGO.mkdir(parents=True)
    (CWD_EGO / "config.yaml").write_text(config.model_dump_json(indent=2), encoding="utf-8")
    (CWD_EGO / "manifest.yaml").write_text(
        manifest.model_dump_json(indent=2), encoding="utf-8"
    )
    (CWD_EGO / "runs").mkdir()
    (CWD_EGO / "cache" / "sol").mkdir(parents=True)
    # progress.json — пустой
    (CWD_EGO / "progress.json").write_text(
        Progress().model_dump_json(indent=2), encoding="utf-8"
    )
