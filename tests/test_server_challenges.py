"""Challenge stages through the API — POST /check with ``files``, GET /challenges (ADR-0018 D18.5).

The fixture catalog ``tests/fixtures/challenges_catalog`` holds one challenge
with two stages (``KV01`` — import mode, ``KV02`` — black-box ``@program``).
A stage submission is ``{"files": {path: source}}``; it runs the tests of
stages 1..N and writes progress for stage N only. An ordinary task stays on
``student_code``: the old flow must not change.
"""

from __future__ import annotations

import importlib
import json
import os
import sqlite3
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

FIXTURE_CATALOG = Path(__file__).parent / "fixtures" / "challenges_catalog"
KV_FOLDER = FIXTURE_CATALOG / "projects" / "kv-track" / "folders" / "kv_store"

#: A stage-1 project: only ``parse_command``, the rest of the starter is not
#: needed by stage 1's import-mode tests.
STAGE1_FILES = {
    "commands.py": (
        "def parse_command(line):\n"
        "    parts = line.split()\n"
        "    if not parts:\n"
        "        return 'EXIT', None\n"
        "    return parts[0].upper(), parts[1:] or None\n"
    ),
    "main.py": "print('stage 1')\n",
}

#: The stage-2 reference project (loop + JSON storage) — passes stages 1..2.
STAGE2_FILES = {
    path.relative_to(KV_FOLDER / "solution").as_posix(): path.read_text(encoding="utf-8")
    for path in sorted((KV_FOLDER / "solution").rglob("*"))
    if path.is_file()
}


@pytest.fixture
def temp_db(monkeypatch):
    tmp = Path(tempfile.mkdtemp()) / "test.db"
    monkeypatch.setenv("EGO_DB_PATH", str(tmp))
    import ego_server.config
    import ego_server.db

    importlib.reload(ego_server.config)
    importlib.reload(ego_server.db)
    ego_server.db.init_db()
    yield tmp


@pytest.fixture
def client(temp_db, monkeypatch):
    import ego_server.main

    importlib.reload(ego_server.main)
    from ego_server.sync import sync_from_path

    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    result = sync_from_path(conn, FIXTURE_CATALOG, source="manual")
    conn.commit()
    conn.close()
    assert result.errors == 0, result.error_details

    with TestClient(ego_server.main.app) as c:
        yield c


def _register_and_login(client, username="alice", password="pw", role="student"):
    if role != "student":
        from tests.conftest import create_test_user

        return create_test_user(client, username, password, role)
    r = client.post(
        "/auth/register",
        json={"username": username, "password": password, "role": role},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"], r.json()["user_id"]


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def _check(client, token, task_id, **body):
    return client.post(
        "/check", json={"task_id": task_id, **body}, headers=_auth_headers(token)
    )


def _progress(temp_db, student_id):
    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    try:
        return {
            row["task_id"]: dict(row)
            for row in conn.execute(
                "SELECT * FROM progress WHERE student_id = ?", (student_id,)
            ).fetchall()
        }
    finally:
        conn.close()


# === POST /check with files ===


def test_check_stage_with_files_returns_stage_results(client):
    token, _ = _register_and_login(client)
    r = _check(client, token, "KV01", files=STAGE1_FILES)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["task_id"] == "KV01"
    assert data["status"] == "passed"
    assert data["total_tests"] > 0
    assert all(tr["stage"] == 1 for tr in data["results"])
    assert all(tr["stage_title"] == "Разбор команды" for tr in data["results"])
    assert "Этап 1: Разбор команды" in data["log"]
    # Project hash, not a single-file hash of a function.
    assert len(data["solution_hash"]) == 64


def test_check_stage_runs_the_previous_stages(client):
    """Stage 2 runs stages 1..2: a broken ``commands.py`` fails both (D18.2)."""
    token, _ = _register_and_login(client)
    r = _check(client, token, "KV02", files=STAGE2_FILES)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["status"] == "passed"
    assert {tr["stage"] for tr in data["results"]} == {1, 2}

    broken = dict(STAGE2_FILES)
    broken["commands.py"] = "def parse_command(line):\n    return line\n"
    r = _check(client, token, "KV02", files=broken)
    assert r.status_code == 200, r.text
    failed = [tr for tr in r.json()["results"] if not tr["passed"]]
    # Stage 1's import cases fail, and stage 2's program runs fail with them.
    assert {tr["stage"] for tr in failed} == {1, 2}
    assert r.json()["status"] != "passed"


def test_only_the_later_stage_can_fail(client):
    """A project that passes stage 1 but not stage 2 fails stage 2 alone."""
    token, _ = _register_and_login(client)
    files = {"commands.py": STAGE2_FILES["commands.py"], "main.py": "print('nope')\n"}
    r = _check(client, token, "KV02", files=files)
    assert r.status_code == 200, r.text
    data = r.json()
    passed_stages = {tr["stage"] for tr in data["results"] if tr["passed"]}
    failed_stages = {tr["stage"] for tr in data["results"] if not tr["passed"]}
    assert passed_stages == {1}
    assert failed_stages == {2}



def test_check_stage_passes_files_to_the_program_run(client):
    """``@program`` with ``files`` / ``expect_files``: the store survives the run."""
    token, _ = _register_and_login(client)
    data = _check(client, token, "KV02", files=STAGE2_FILES).json()
    by_description = {tr["description"]: tr for tr in data["results"]}
    assert by_description["SET, потом GET"]["passed"] is True


# === 422: exactly one of student_code / files ===


def test_check_stage_with_student_code_is_rejected_with_update_hint(client):
    token, _ = _register_and_login(client)
    r = _check(client, token, "KV01", student_code="def task_kv01_parse():\n    ...\n")
    assert r.status_code == 422
    assert "обнови расширение" in r.json()["detail"]


def test_check_requires_one_of_student_code_or_files(client):
    token, _ = _register_and_login(client)
    r = _check(client, token, "KV01")
    assert r.status_code == 422
    assert "files" in r.json()["detail"]
    assert "student_code" in r.json()["detail"]


def test_check_stage_rejects_both_student_code_and_files(client):
    token, _ = _register_and_login(client)
    r = _check(client, token, "KV01", student_code="pass", files=STAGE1_FILES)
    assert r.status_code == 422
    assert "student_code" in r.json()["detail"] and "files" in r.json()["detail"]


def test_check_stage_rejects_an_empty_project(client):
    """An empty ``files`` would "pass" trivially; it is not a submission."""
    token, _ = _register_and_login(client)
    r = _check(client, token, "KV01", files={})
    assert r.status_code == 422
    assert "files пустой" in r.json()["detail"]


def test_check_stage_rejects_non_string_file_content(client):
    token, _ = _register_and_login(client)
    r = _check(client, token, "KV01", files={"main.py": 42})
    assert r.status_code == 422


@pytest.fixture
def legacy_task(client):
    """Import the legacy ``docs/tasks`` corpus so an ordinary task exists too."""
    from ego_server.cli import main as cli_main

    cwd = Path.cwd()
    try:
        os.chdir(Path(__file__).parent.parent)
        cli_main(["admin", "import-tasks", "--docs-dir", "docs/tasks"])
    finally:
        os.chdir(cwd)
    return "F1"


def test_check_ordinary_task_rejects_files(client, legacy_task):
    """An ordinary task takes only ``student_code`` (no challenge stage)."""
    token, _ = _register_and_login(client)
    r = _check(client, token, legacy_task, files={"main.py": "print('x')\n"})
    assert r.status_code == 422
    assert "челленджа" in r.json()["detail"]


@pytest.mark.parametrize(
    ("files", "fragment"),
    [
        ({"../evil.py": "", "main.py": ""}, "`..` запрещён"),
        ({"/abs.py": ""}, "абсолютный"),
        ({"notes.txt": "x"}, "не входит в проект"),
    ],
)
def test_check_stage_rejects_unsafe_files(client, files, fragment):
    token, _ = _register_and_login(client)
    r = _check(client, token, "KV01", files=files)
    assert r.status_code == 422
    assert fragment in r.json()["detail"]


def test_check_stage_enforces_max_files(client):
    token, _ = _register_and_login(client)
    files = {f"m{index}.py": "x = 1\n" for index in range(21)}
    files["main.py"] = "print('x')\n"
    r = _check(client, token, "KV01", files=files)
    assert r.status_code == 422
    assert "лимита 20" in r.json()["detail"]


def test_check_stage_total_size_limit(client):
    """``max_code_chars`` applies to the whole project view."""
    token, _ = _register_and_login(client)
    huge = dict(STAGE1_FILES)
    # Well above both the default 100000 chars and the 200000-byte workspace cap.
    huge["commands.py"] = STAGE1_FILES["commands.py"] + "#" * 300_000 + "\n"
    r = _check(client, token, "KV01", files=huge)
    assert r.status_code in (413, 422)
    if r.status_code == 413:
        assert "size limit" in r.json()["detail"]
    else:
        assert "байт" in r.json()["detail"]


# === progress only for stage N ===


def test_progress_is_written_only_for_stage_n(client, temp_db):
    token, student_id = _register_and_login(client)
    assert _check(client, token, "KV02", files=STAGE2_FILES).status_code == 200
    rows = _progress(temp_db, student_id)
    assert set(rows) == {"KV02"}
    assert rows["KV02"]["status"] == "passed"
    # Runs are logged for the checked stage only.
    conn = sqlite3.connect(temp_db)
    try:
        run_tasks = [row[0] for row in conn.execute("SELECT task_id FROM runs")]
    finally:
        conn.close()
    assert run_tasks == ["KV02"]


def test_failed_stage_keeps_earlier_progress(client, temp_db):
    token, student_id = _register_and_login(client)
    assert _check(client, token, "KV01", files=STAGE1_FILES).status_code == 200
    broken = dict(STAGE2_FILES)
    broken["main.py"] = "print('nothing')\n"
    assert _check(client, token, "KV02", files=broken).status_code in (200, 422)
    rows = _progress(temp_db, student_id)
    assert rows["KV01"]["status"] == "passed"
    assert rows["KV01"]["attempts"] == 1  # not touched by the stage-2 check
    assert rows["KV02"]["status"] != "passed"


# === runs.files_json ===


def test_runs_store_the_whole_project(client, temp_db):
    token, student_id = _register_and_login(client)
    assert _check(client, token, "KV01", files=STAGE1_FILES).status_code == 200
    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    try:
        (row,) = conn.execute(
            "SELECT * FROM runs WHERE student_id = ?", (student_id,)
        ).fetchall()
    finally:
        conn.close()
    assert json.loads(row["files_json"]) == STAGE1_FILES
    # The history log groups results by stage.
    assert "Этап 1: Разбор команды" in row["log"]


def test_ordinary_check_stores_no_files_json(client, temp_db, legacy_task):
    """A single-file task keeps the old flow: ``student_code``, no stage fields."""
    token, student_id = _register_and_login(client)
    student = "def task_f1_find_critical(logs):\n    return None\n"
    r = _check(client, token, legacy_task, student_code=student)
    assert r.status_code == 200, r.text
    assert r.json()["results"]
    for tr in r.json()["results"]:
        # Exactly the pre-ADR-0018 row shape, byte for byte.
        assert set(tr) == {"description", "passed", "expected_repr", "actual_repr", "error"}
    conn = sqlite3.connect(temp_db)
    try:
        (files_json,) = conn.execute(
            "SELECT files_json FROM runs WHERE student_id = ?", (student_id,)
        ).fetchone()
    finally:
        conn.close()
    assert files_json is None


# === GET /challenges/<folder_id> ===


def test_get_challenge_requires_auth(client):
    assert client.get("/challenges/kv_store").status_code == 401


def test_get_challenge_metadata_and_stages(client):
    token, _ = _register_and_login(client)
    r = client.get("/challenges/kv_store", headers=_auth_headers(token))
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["id"] == "kv_store"
    assert data["project_id"] == "kv-track"
    assert data["workspace"] == {
        "entry": "main.py",
        "include": ["*.py", "data/*.json"],
        "max_files": 20,
        "max_bytes": 200000,
    }
    assert [stage["id"] for stage in data["stages"]] == ["KV01", "KV02"]
    assert [stage["number"] for stage in data["stages"]] == [1, 2]
    assert [stage["title"] for stage in data["stages"]] == [
        "Разбор команды",
        "Сохранение в JSON",
    ]
    assert [stage["status"] for stage in data["stages"]] == ["new", "new"]
    assert [stage["current"] for stage in data["stages"]] == [True, False]
    assert set(data["starter"]) == {"commands.py", "main.py"}
    assert "def parse_command" in data["starter"]["commands.py"]


def test_get_challenge_unknown_is_404(client):
    token, _ = _register_and_login(client)
    r = client.get("/challenges/nope", headers=_auth_headers(token))
    assert r.status_code == 404


def test_get_challenge_shows_stage_status_after_check(client):
    token, _ = _register_and_login(client)
    assert _check(client, token, "KV01", files=STAGE1_FILES).status_code == 200
    data = client.get("/challenges/kv_store", headers=_auth_headers(token)).json()
    statuses = {stage["id"]: stage["status"] for stage in data["stages"]}
    assert statuses == {"KV01": "passed", "KV02": "new"}
    # «Начать» jumps to the first stage that is not passed yet.
    assert [stage["current"] for stage in data["stages"]] == [False, True]


def test_ordinary_folder_is_not_a_challenge(client):
    """``GET /challenges`` only serves ``kind: challenge`` folders."""
    token, _ = _register_and_login(client)
    r = client.get("/challenges/kv-track", headers=_auth_headers(token))
    assert r.status_code == 404
