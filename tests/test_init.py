"""Tests for `ego init` and progress persistence (beads ego-trainer-8bv.1)."""

import json

import pytest

from ego.cli.main import main


# Models are implemented in parallel by beads ego-trainer-93h.2.
# If they are not ready yet, skip the model-dependent tests gracefully.
try:
    from ego.models import Config, Manifest, Progress, ProgressEntry  # noqa: F401

    _MODELS_READY = True
except Exception:  # noqa: BLE001 — ImportError or NotImplementedError from stub
    _MODELS_READY = False

_skip_no_models = pytest.mark.skipif(
    not _MODELS_READY, reason="waiting for ego.models (beads ego-trainer-93h.2)"
)


@pytest.fixture
def tmp_cwd(tmp_path, monkeypatch):
    """Run commands in a temp directory."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


@_skip_no_models
def test_init_local_creates_ego_dir(tmp_cwd):
    rc = main(["init", "--local"])
    assert rc == 0
    ego = tmp_cwd / ".ego"
    assert ego.exists()
    assert (ego / "config.yaml").exists()
    assert (ego / "manifest.yaml").exists()
    assert (ego / "progress.json").exists()
    assert (ego / "runs").is_dir()
    assert (ego / "cache" / "sol").is_dir()


@_skip_no_models
def test_init_local_config_content(tmp_cwd):
    rc = main(["init", "--local"])
    assert rc == 0
    config = json.loads((tmp_cwd / ".ego" / "config.yaml").read_text(encoding="utf-8"))
    assert config["server_url"] == ""
    assert config["student_username"] == "local-user"
    assert config["role"] == "student"


@_skip_no_models
def test_init_refuses_existing(tmp_cwd):
    (tmp_cwd / ".ego").mkdir()
    rc = main(["init", "--local"])
    assert rc == 1


@_skip_no_models
def test_init_force_overwrites(tmp_cwd):
    ego = tmp_cwd / ".ego"
    ego.mkdir()
    (ego / "old.txt").write_text("old")
    rc = main(["init", "--local", "--force"])
    assert rc == 0
    assert not (ego / "old.txt").exists()
    assert (ego / "config.yaml").exists()


@_skip_no_models
def test_progress_load_save_roundtrip(tmp_cwd):
    from ego.progress import load_progress, save_progress

    p = Progress(student_username="test")
    p.upsert(
        ProgressEntry(task_id="F1", version="1.0.0", status="passed", attempts=2)
    )
    save_progress(p)

    loaded = load_progress()
    assert loaded.student_username == "test"
    assert loaded.entries[0].task_id == "F1"
    assert loaded.entries[0].status == "passed"


@_skip_no_models
def test_progress_load_missing_returns_empty(tmp_cwd):
    from ego.progress import load_progress

    p = load_progress()
    assert p.entries == []
