"""Integration tests for ego CLI — covers all existing commands and edge cases.

This complements test_init.py and test_list.py (which focus on init/list
details). Here we cover cross-command behavior, error handling, --help,
--version, unknown commands, and composition scenarios.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from ego.cli.main import main


# === --version ===


def test_version_prints_ego_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "ego" in captured.out
    # Should contain version like 0.1.0 or similar
    assert any(c.isdigit() for c in captured.out)


def test_version_via_subprocess():
    """ego --version should work via subprocess too."""
    r = subprocess.run(
        [sys.executable, "-m", "ego.cli.main", "--version"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0
    assert "ego" in r.stdout


# === --help / no args ===


def test_no_args_prints_help_and_exits_0(capsys):
    rc = main([])
    assert rc == 0
    captured = capsys.readouterr()
    assert "ego" in captured.out.lower() or "usage" in captured.out.lower()


def test_help_prints_subcommands(capsys):
    # argparse exits with 0 on --help (raises SystemExit).
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "init" in captured.out
    assert "list" in captured.out
    assert "check" in captured.out
    assert "pull" in captured.out
    assert "push" in captured.out


# === Unknown command ===


def test_unknown_command_exits_nonzero(capsys):
    with pytest.raises(SystemExit):
        main(["foobar"])
    # argparse rejects unknown subcommands with SystemExit(2)


# === Stub commands (check/pull/push) ===


def test_check_not_implemented_returns_1(capsys):
    rc = main(["check"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "not implemented" in captured.err.lower()


def test_pull_not_implemented_returns_1(capsys):
    rc = main(["pull"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "not implemented" in captured.err.lower()


def test_push_not_implemented_returns_1(capsys):
    rc = main(["push"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "not implemented" in captured.err.lower()


# === Composition: init then list ===


def test_init_then_list_offline(tmp_path, monkeypatch, capsys):
    """init --local then list --local should show the scanned tasks."""
    monkeypatch.chdir(tmp_path)
    # First create docs/tasks/ with a few files
    (tmp_path / "docs" / "tasks" / "block_f_simple").mkdir(parents=True)
    (tmp_path / "docs" / "tasks" / "block_f_simple" / "task_f1.md").write_text("# F1")
    (tmp_path / "docs" / "tasks" / "block_f_simple" / "task_f2.md").write_text("# F2")

    # init
    rc = main(["init", "--local"])
    assert rc == 0
    capsys.readouterr()  # clear

    # list --local (offline, scans docs/tasks/)
    rc = main(["list", "--local"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "F1" in captured.out
    assert "F2" in captured.out


def test_init_then_list_with_manifest(tmp_path, monkeypatch, capsys):
    """init --local then list (with manifest entries) should show pulled tasks."""
    monkeypatch.chdir(tmp_path)
    rc = main(["init", "--local"])
    assert rc == 0
    # Add a fake manifest entry
    manifest_path = tmp_path / ".ego" / "manifest.yaml"
    manifest = {
        "tasks": [
            {"id": "F1", "block": "F", "slug": "block_f_simple", "task_id": "F1",
             "version": "1.0.0", "content_hash": "abc",
             "pulled_at": "2026-07-19T12:00:00", "md_path": "tasks/F/F1.md",
             "md_modified": False, "stub_modified": False},
        ],
        "server_version": "0.1.0",
        "last_pull_at": "2026-07-19T12:00:00",
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    capsys.readouterr()
    rc = main(["list"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "F1" in captured.out


# === Error handling ===


def test_init_refuses_existing_then_force(tmp_path, monkeypatch, capsys):
    """init without --force on existing .ego/ fails; --force overwrites."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".ego").mkdir()
    (tmp_path / ".ego" / "old.txt").write_text("old")

    rc = main(["init", "--local"])
    assert rc == 1
    assert (tmp_path / ".ego" / "old.txt").exists()  # not overwritten

    rc = main(["init", "--local", "--force"])
    assert rc == 0
    assert not (tmp_path / ".ego" / "old.txt").exists()
    assert (tmp_path / ".ego" / "config.yaml").exists()


# === Argument validation ===


def test_init_with_server_url(tmp_path, monkeypatch, capsys):
    """init with --server-url should set server_url in config."""
    monkeypatch.chdir(tmp_path)
    rc = main(["init", "--server-url", "http://ego.example.com:8000"])
    assert rc == 0
    config = json.loads((tmp_path / ".ego" / "config.yaml").read_text(encoding="utf-8"))
    assert config["server_url"] == "http://ego.example.com:8000"


# === Subprocess integration ===


def test_ego_runs_via_subprocess():
    """`uv run ego --version` (or via -m) should work."""
    r = subprocess.run(
        [sys.executable, "-m", "ego.cli.main"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0


def test_ego_init_via_subprocess(tmp_path, monkeypatch):
    """init via subprocess should create .ego/."""
    monkeypatch.chdir(tmp_path)
    r = subprocess.run(
        [sys.executable, "-m", "ego.cli.main", "init", "--local"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0
    assert (tmp_path / ".ego" / "config.yaml").exists()


# === Idempotency ===


def test_double_init_local_idempotent_with_force(tmp_path, monkeypatch):
    """Running init --local twice with --force should produce same state."""
    monkeypatch.chdir(tmp_path)
    main(["init", "--local"])
    config1 = (tmp_path / ".ego" / "config.yaml").read_text(encoding="utf-8")
    main(["init", "--local", "--force"])
    config2 = (tmp_path / ".ego" / "config.yaml").read_text(encoding="utf-8")
    assert config1 == config2


# === Files created by init ===


def test_init_creates_required_files(tmp_path, monkeypatch):
    """init --local should create all expected files/dirs."""
    monkeypatch.chdir(tmp_path)
    main(["init", "--local"])
    ego = tmp_path / ".ego"
    assert (ego / "config.yaml").is_file()
    assert (ego / "manifest.yaml").is_file()
    assert (ego / "progress.json").is_file()
    assert (ego / "runs").is_dir()
    assert (ego / "cache" / "sol").is_dir()


def test_init_progress_json_is_valid(tmp_path, monkeypatch):
    """progress.json after init should be valid Progress JSON."""
    monkeypatch.chdir(tmp_path)
    main(["init", "--local"])
    progress = json.loads((tmp_path / ".ego" / "progress.json").read_text(encoding="utf-8"))
    assert "entries" in progress
    assert progress["entries"] == []


def test_init_manifest_yaml_is_valid(tmp_path, monkeypatch):
    """manifest.yaml after init should be valid Manifest JSON."""
    monkeypatch.chdir(tmp_path)
    main(["init", "--local"])
    manifest = json.loads((tmp_path / ".ego" / "manifest.yaml").read_text(encoding="utf-8"))
    assert "tasks" in manifest
    assert manifest["tasks"] == []


# === list edge cases ===


def test_list_offline_empty_docs_tasks(tmp_path, monkeypatch, capsys):
    """list --local with empty docs/tasks/ should error."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "docs" / "tasks").mkdir(parents=True)
    rc = main(["list", "--local"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "no" in captured.err.lower() or "no .md" in captured.out.lower()


def test_list_offline_no_docs_dir(tmp_path, monkeypatch, capsys):
    """list --local without docs/tasks/ dir should error."""
    monkeypatch.chdir(tmp_path)
    rc = main(["list", "--local"])
    assert rc == 1


def test_list_offline_multiple_blocks(tmp_path, monkeypatch, capsys):
    """list --local should show tasks from all blocks, sorted by block/task."""
    monkeypatch.chdir(tmp_path)
    for block in ("block_f_simple", "block_1_logs", "block_h_more_domains"):
        d = tmp_path / "docs" / "tasks" / block
        d.mkdir(parents=True)
        for n in ("1", "2"):
            (d / f"task_x{n}.md").write_text(f"# X{n}")
    rc = main(["list", "--local"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "1" in captured.out
    assert "F" in captured.out
    assert "H" in captured.out


# === Full 33-task scenario ===


def test_list_local_repo_root(capsys):
    """list --local at repo root should show all 33 tasks (no .ego/ needed)."""
    # main() uses cwd, so we need to chdir to repo root
    import os
    repo_root = Path(__file__).parent.parent
    old_cwd = os.getcwd()
    try:
        os.chdir(repo_root)
        rc = main(["list", "--local"])
        assert rc == 0
        captured = capsys.readouterr()
        # 33 tasks found
        assert "33" in captured.out
    finally:
        os.chdir(old_cwd)
