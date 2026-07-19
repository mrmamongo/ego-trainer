"""Tests for `ego list` (task ego-trainer-8bv.6)."""

import json

import pytest

from ego.cli.main import main


@pytest.fixture
def tmp_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_list_offline_no_docs_tasks(tmp_cwd, capsys):
    rc = main(["list", "--local"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "docs/tasks" in captured.err or "docs/tasks" in captured.out


def test_list_offline_scans_docs_tasks(tmp_cwd, capsys):
    # Create a fake docs/tasks/ structure.
    (tmp_cwd / "docs" / "tasks" / "block_f_simple").mkdir(parents=True)
    (tmp_cwd / "docs" / "tasks" / "block_f_simple" / "task_f1.md").write_text("# F1")
    (tmp_cwd / "docs" / "tasks" / "block_f_simple" / "task_f2.md").write_text("# F2")
    (tmp_cwd / "docs" / "tasks" / "block_1_logs").mkdir(parents=True)
    (tmp_cwd / "docs" / "tasks" / "block_1_logs" / "task_1_5.md").write_text("# 1.5")

    rc = main(["list", "--local"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "F1" in captured.out
    assert "F2" in captured.out
    assert "1.5" in captured.out
    assert "F" in captured.out  # block letter


def test_list_no_manifest_no_local(tmp_cwd, capsys):
    rc = main(["list"])
    # No manifest and not --local: falls back to offline scan; with no
    # docs/tasks/ that returns 1. Either way it must not traceback.
    assert rc in (0, 1)


def test_list_with_manifest(tmp_cwd, capsys):
    # Create .ego/ with a manifest and progress.
    ego = tmp_cwd / ".ego"
    ego.mkdir()
    manifest = {
        "tasks": [
            {
                "id": "F1",
                "block": "F",
                "slug": "block_f_simple",
                "task_id": "F1",
                "version": "1.0.0",
                "content_hash": "abc",
                "pulled_at": "2026-07-19T12:00:00",
                "md_path": "tasks/F/F1.md",
                "md_modified": False,
                "stub_modified": False,
            },
        ],
        "server_version": "0.1.0",
        "last_pull_at": "2026-07-19T12:00:00",
    }
    (ego / "manifest.yaml").write_text(json.dumps(manifest), encoding="utf-8")
    (ego / "progress.json").write_text(
        json.dumps(
            {
                "student_username": "ivan",
                "entries": [
                    {
                        "task_id": "F1",
                        "version": "1.0.0",
                        "status": "passed",
                        "attempts": 3,
                        "passed_tests": 5,
                        "total_tests": 5,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    rc = main(["list"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "F1" in captured.out
    assert "passed" in captured.out
    assert "3" in captured.out  # attempts


def test_block_letter_helper():
    from ego.cli.list_cmd import _block_letter

    assert _block_letter("block_f_simple") == "F"
    assert _block_letter("block_1_logs") == "1"
    assert _block_letter("block_a_join") == "A"
    assert _block_letter("block_h_more_domains") == "H"


def test_task_id_from_name_helper():
    from ego.cli.list_cmd import _task_id_from_name

    assert _task_id_from_name("task_f1") == "F1"
    assert _task_id_from_name("task_1_5") == "1.5"
    assert _task_id_from_name("task_a") == "A"
    assert _task_id_from_name("task_h8") == "H8"
