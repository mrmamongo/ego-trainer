"""Tests for ego_tui.cli — start/list/show commands."""

from __future__ import annotations

from pathlib import Path

import pytest

from ego_tui.cli import _find_task_md, main


# === --version / --help ===


def test_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "ego-tui" in captured.out


def test_help_prints_subcommands(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "start" in captured.out
    assert "list" in captured.out
    assert "show" in captured.out


def test_no_args_prints_help(capsys):
    rc = main([])
    assert rc == 0
    captured = capsys.readouterr()
    assert "ego-tui" in captured.out.lower() or "usage" in captured.out.lower()


# === start ===


def test_start_returns_1_with_helpful_message(capsys):
    rc = main(["start"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "not yet implemented" in captured.err.lower() or "x4f.1" in captured.err


def test_start_with_task_arg(capsys):
    rc = main(["start", "--task", "F1"])
    assert rc == 1  # not implemented
    captured = capsys.readouterr()
    assert "x4f.1" in captured.err or "not yet implemented" in captured.err.lower()


# === list (delegates to ego.cli.list_cmd) ===


def test_list_local_with_docs_tasks(capsys, monkeypatch):
    """ego-tui list --local should work like ego list --local."""
    repo_root = Path(__file__).parent.parent
    monkeypatch.chdir(repo_root)
    rc = main(["list", "--local"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "F1" in captured.out
    assert "33" in captured.out  # 33 tasks


def test_list_local_no_docs(capsys, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rc = main(["list", "--local"])
    assert rc == 1


# === show ===


def test_show_f1_local(capsys, monkeypatch):
    """ego-tui show F1 --local should print the .md content."""
    repo_root = Path(__file__).parent.parent
    monkeypatch.chdir(repo_root)
    rc = main(["show", "F1", "--local"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "F1" in captured.out or "критический" in captured.out.lower() or "Задача" in captured.out


def test_show_1_5_local(capsys, monkeypatch):
    """ego-tui show 1.5 --local should work for period-containing id."""
    repo_root = Path(__file__).parent.parent
    monkeypatch.chdir(repo_root)
    rc = main(["show", "1.5", "--local"])
    assert rc == 0


def test_show_nonexistent_task_returns_1(capsys, monkeypatch):
    repo_root = Path(__file__).parent.parent
    monkeypatch.chdir(repo_root)
    rc = main(["show", "ZZZ", "--local"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "not found" in captured.err.lower() or "ZZZ" in captured.err


def test_show_h8_local(capsys, monkeypatch):
    repo_root = Path(__file__).parent.parent
    monkeypatch.chdir(repo_root)
    rc = main(["show", "H8", "--local"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "H8" in captured.out or "синтез" in captured.out.lower() or "Задача" in captured.out


# === _find_task_md helper ===


def test_find_task_md_f1_local(monkeypatch):
    repo_root = Path(__file__).parent.parent
    monkeypatch.chdir(repo_root)
    candidates = _find_task_md("F1", local=True)
    assert len(candidates) >= 1
    assert candidates[0].name == "task_f1.md"


def test_find_task_md_1_5_normalizes_period(monkeypatch):
    repo_root = Path(__file__).parent.parent
    monkeypatch.chdir(repo_root)
    candidates = _find_task_md("1.5", local=True)
    assert len(candidates) >= 1
    assert "task_1_5.md" in str(candidates[0])


def test_find_task_md_a_uppercase(monkeypatch):
    repo_root = Path(__file__).parent.parent
    monkeypatch.chdir(repo_root)
    candidates = _find_task_md("A", local=True)
    assert len(candidates) >= 1
    assert "task_a.md" in str(candidates[0])


def test_find_task_md_nonexistent(monkeypatch):
    repo_root = Path(__file__).parent.parent
    monkeypatch.chdir(repo_root)
    candidates = _find_task_md("ZZZ", local=True)
    assert len(candidates) == 0


def test_find_task_md_h8(monkeypatch):
    repo_root = Path(__file__).parent.parent
    monkeypatch.chdir(repo_root)
    candidates = _find_task_md("H8", local=True)
    assert len(candidates) >= 1
    assert "task_h8.md" in str(candidates[0])


# === Integration with ego pull (when cache exists) ===


def test_show_uses_cache_when_available(tmp_path, monkeypatch, capsys):
    """If .ego/cache/cond/<id>.md exists, show should use it (not --local)."""
    monkeypatch.chdir(tmp_path)
    cache = tmp_path / ".ego" / "cache" / "cond"
    cache.mkdir(parents=True)
    (cache / "F1.md").write_text("# Cached F1\nThis is from cache.", encoding="utf-8")
    rc = main(["show", "F1"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Cached F1" in captured.out or "from cache" in captured.out.lower()


def test_show_local_ignores_cache(tmp_path, monkeypatch, capsys):
    """--local should ignore cache and read from docs/tasks/."""
    cache = tmp_path / ".ego" / "cache" / "cond"
    cache.mkdir(parents=True)
    (cache / "F1.md").write_text("# From cache", encoding="utf-8")

    docs = tmp_path / "docs" / "tasks" / "block_f_simple"
    docs.mkdir(parents=True)
    (docs / "task_f1.md").write_text("# From docs/tasks", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    rc = main(["show", "F1", "--local"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "From docs/tasks" in captured.out
    assert "From cache" not in captured.out
