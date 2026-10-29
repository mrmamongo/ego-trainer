"""Staged checking of multi-file challenges — ``run_stage_check`` (ADR-0018 D18.2/D18.3).

Stage N is checked by running the tests of stages 1..N over the student's
project; every result names its stage (``stage`` / ``stage_title``) and the
log is grouped by stage. Static ``@rules`` see the whole project's ``.py``
files, general rules per file and ``file=`` rules on one file only.

The stages come from the fixture catalog ``tests/fixtures/challenges_catalog``,
parsed exactly as the server does it.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

from ego.checker import StageTests, format_stage_check_result, run_stage_check
from ego.content_repo import discover_repo, read_project_files
from ego.parser import parse_task_file

FIXTURE_CATALOG = Path(__file__).parent / "fixtures" / "challenges_catalog"
KV_FOLDER = FIXTURE_CATALOG / "projects" / "kv-track" / "folders" / "kv_store"


@pytest.fixture(scope="module")
def challenge():
    """The fixture challenge: its workspace spec and parsed stages 1..N."""
    (folder,) = discover_repo(FIXTURE_CATALOG).challenge_folders
    workspace = folder.folder.workspace.model_dump()
    stages = [
        StageTests(
            task=parse_task_file(item.md_path),
            number=item.stage,
            title=item.frontmatter.title,
        )
        for item in sorted(folder.tasks, key=lambda task: task.stage)
    ]
    return workspace, stages


@pytest.fixture(scope="module")
def solution() -> dict[str, str]:
    """The reference project (passes every stage)."""
    return read_project_files(KV_FOLDER / "solution", ["*.py", "data/*.json"])


def _stage(stages: list[StageTests], number: int) -> StageTests:
    return stages[number - 1]


# === regression across stages ===


def test_reference_solution_passes_every_stage(challenge, solution):
    workspace, stages = challenge
    for stage in stages:
        result = run_stage_check(stage.task, solution, stages=stages, workspace=workspace)
        assert result.all_passed, [(tr.description, tr.error) for tr in result.results]
        assert result.status == "passed"
        # Stage N runs the tests of stages 1..N, no more.
        assert {tr.stage for tr in result.results} == set(range(1, stage.number + 1))


def test_stage_two_runs_stage_one_too(challenge, solution):
    """D18.2: the stage-2 check repeats stage 1's import cases."""
    workspace, stages = challenge
    result = run_stage_check(_stage(stages, 2).task, solution, stages=stages, workspace=workspace)
    stage_1 = [tr for tr in result.results if tr.stage == 1]
    stage_2 = [tr for tr in result.results if tr.stage == 2]
    assert stage_1 and stage_2
    assert all(tr.stage_title == "Разбор команды" for tr in stage_1)
    assert all(tr.stage_title == "Сохранение в JSON" for tr in stage_2)


def test_regression_in_an_earlier_stage_fails_the_later_one(challenge, solution):
    """A broken ``commands.py`` while doing stage 2 fails the stage-2 check."""
    workspace, stages = challenge
    broken = dict(solution)
    broken["commands.py"] = "def parse_command(line):\n    return line\n"
    result = run_stage_check(_stage(stages, 2).task, broken, stages=stages, workspace=workspace)
    assert not result.all_passed
    assert result.status != "passed"
    assert result.failed_stages == [1, 2]
    assert all(not tr.passed for tr in result.results if tr.stage == 1)


def test_only_the_later_stage_can_fail(challenge, solution):
    """A project that passes stage 1 but not stage 2 fails stage 2 alone."""
    workspace, stages = challenge
    files = {"commands.py": solution["commands.py"], "main.py": "print('nope')\n"}
    result = run_stage_check(_stage(stages, 2).task, files, stages=stages, workspace=workspace)
    assert result.failed_stages == [2]
    assert all(tr.passed for tr in result.results if tr.stage == 1)


def test_stage_one_only_runs_stage_one(challenge):
    """Stage 1 checks the starter's import cases, not stage 2's ``@program``."""
    workspace, stages = challenge
    starter = read_project_files(KV_FOLDER / "starter", ["*.py"])
    result = run_stage_check(_stage(stages, 1).task, starter, stages=stages, workspace=workspace)
    assert {tr.stage for tr in result.results} == {1}
    assert not result.all_passed  # the starter's ``parse_command`` is a stub


def test_unknown_stage_is_rejected(challenge, solution):
    """``stage_task`` must be one of ``stages`` (a server-side wiring bug)."""
    workspace, stages = challenge
    other = StageTests(task=_stage(stages, 1).task, number=1, title="Чужой этап")
    with pytest.raises(ValueError, match="не найден"):
        run_stage_check(other.task, solution, stages=stages[1:], workspace=workspace)


def test_invalid_files_raise_with_all_russian_errors(challenge):
    workspace, stages = challenge
    with pytest.raises(ValueError, match="`..` запрещён"):
        run_stage_check(
            _stage(stages, 1).task, {"../x.py": ""}, stages=stages, workspace=workspace
        )


def test_invalid_level_filter_is_rejected(challenge, solution):
    workspace, stages = challenge
    with pytest.raises(ValueError, match="level"):
        run_stage_check(
            _stage(stages, 1).task, solution, stages=stages, workspace=workspace, level="nope"
        )


# === stage fields and the log ===


def test_every_result_carries_its_stage_and_title(challenge, solution):
    workspace, stages = challenge
    result = run_stage_check(_stage(stages, 2).task, solution, stages=stages, workspace=workspace)
    assert result.results
    for tr in result.results:
        assert tr.stage in (1, 2)
        assert tr.stage_title == _stage(stages, tr.stage).title


def test_program_case_of_the_last_stage(challenge, solution):
    """``@program`` with ``files`` / ``expect_files`` runs in the project copy."""
    workspace, stages = challenge
    result = run_stage_check(_stage(stages, 2).task, solution, stages=stages, workspace=workspace)
    by_description = {tr.description: tr for tr in result.results}
    repl = by_description["SET, потом GET"]
    assert repl.passed and repl.stage == 2
    assert repl.actual_repr.splitlines() == ["OK", "1"]


def test_format_stage_check_result_groups_by_stage(challenge, solution):
    workspace, stages = challenge
    result = run_stage_check(_stage(stages, 2).task, solution, stages=stages, workspace=workspace)
    log = format_stage_check_result(result)
    assert "Этап 1: Разбор команды — 3/3, пройден" in log
    assert "Этап 2: Сохранение в JSON — 3/3, пройден" in log
    assert log.index("Этап 1") < log.index("Этап 2")


def test_format_stage_check_result_marks_a_failure(challenge):
    workspace, stages = challenge
    files = {"commands.py": "def parse_command(line):\n    return line\n", "main.py": ""}
    result = run_stage_check(_stage(stages, 1).task, files, stages=stages, workspace=workspace)
    log = format_stage_check_result(result)
    assert "не пройден" in log
    assert "x " in log


def test_result_summary_describes_the_whole_run(challenge, solution):
    """``status``/``total_tests`` count stages 1..N (progress is written from them)."""
    workspace, stages = challenge
    first = run_stage_check(_stage(stages, 1).task, solution, stages=stages, workspace=workspace)
    second = run_stage_check(_stage(stages, 2).task, solution, stages=stages, workspace=workspace)
    assert second.total_tests > first.total_tests
    assert second.passed_tests == second.total_tests
    # The submission hash covers the whole project, not one function.
    assert second.solution_hash == first.solution_hash
    assert len(second.solution_hash) == 64


# === static rules over the project ===

RULES_STAGE_1 = """\
from ego.testing import case, rules

@rules(require_functions=["parse_command"], forbid_imports=["json"])
@case(
    target="commands.parse_command",
    args=("get",),
    expected=("GET", None),
    description="команда без аргументов",
)
def task_stage_01_rules():
    ...
"""

RULES_STAGE_2 = """\
from ego.testing import program, rules

@rules(forbid_imports=["json"])
@program(stdin="EXIT\\n", expected_stdout="", description="пустой запуск")
def task_stage_02_rules():
    ...
"""

RULES_STAGE_2_SCOPED = """\
from ego.testing import program, rules

@rules(file="commands.py", forbid_imports=["json"])
@program(stdin="EXIT\\n", expected_stdout="", description="пустой запуск")
def task_stage_02_scoped():
    ...
"""

COMMANDS = "def parse_command(line):\n    parts = line.split()\n    return parts[0].upper(), None\n"


@pytest.fixture
def rules_challenge(tmp_path):
    """Two stages whose tests declare project-wide and file-scoped rules."""
    folder = tmp_path / "challenge"
    folder.mkdir()
    for number, body in (
        (1, RULES_STAGE_1),
        (2, RULES_STAGE_2),
        (3, RULES_STAGE_2_SCOPED),
    ):
        md = folder / f"stage_0{number}_rules.md"
        md.write_text(f"# Задача R0{number}: Правила\n## Условие\n", encoding="utf-8")
        (folder / f"stage_0{number}_rules.tests.py").write_text(body, encoding="utf-8")
    stages = []
    for number in (1, 2, 3):
        task = parse_task_file(folder / f"stage_0{number}_rules.md")
        stages.append(StageTests(task=task, number=number, title=task.title))
    return folder, stages


def test_project_rules_pass_a_clean_project(rules_challenge):
    _folder, stages = rules_challenge
    files = {"commands.py": COMMANDS, "main.py": "print('ok')\n"}
    result = run_stage_check(stages[-1].task, files, stages=stages, timeout=10)
    rule_rows = [tr for tr in result.results if tr.description.startswith("Правило")]
    assert rule_rows == []
    assert result.all_passed, [(tr.description, tr.error) for tr in result.results]


def test_project_rules_see_every_py_file(rules_challenge):
    """``forbid_imports`` is checked per file: the violation names the file."""
    _folder, stages = rules_challenge
    stage_2 = stages[1]
    files = {"commands.py": COMMANDS, "storage.py": "import json\n", "main.py": ""}
    result = run_stage_check(stage_2.task, files, stages=[stage_2], timeout=10)
    rows = [tr for tr in result.results if not tr.passed and tr.description.startswith("Правило")]
    assert [tr.description for tr in rows] == [
        "Правило: `storage.py`: нельзя импортировать `json` (строка 1)"
    ]
    assert rows[0].stage == 2 and rows[0].stage_title == "Правила"


def test_file_scoped_rules_only_apply_to_that_file(rules_challenge):
    """``@rules(file="commands.py")`` does not see ``storage.py``."""
    _folder, stages = rules_challenge
    stage_3 = stages[2]
    files = {"commands.py": COMMANDS, "storage.py": "import json\n", "main.py": ""}
    result = run_stage_check(stage_3.task, files, stages=[stage_3], timeout=10)
    probe = [tr for tr in result.results if not tr.passed and tr.description.startswith("Правило")]
    assert probe == []  # no rule is declared for storage.py in this stage


def test_file_scoped_rules_check_their_own_file(rules_challenge):
    """The scoped rule fires on ``commands.py`` itself."""
    _folder, stages = rules_challenge
    stage_3 = stages[2]
    files = {"commands.py": "import json\n" + COMMANDS, "main.py": ""}
    result = run_stage_check(stage_3.task, files, stages=[stage_3], timeout=10)
    rows = [tr.description for tr in result.results if tr.description.startswith("Правило")]
    assert rows == ["Правило: `commands.py`: нельзя импортировать `json` (строка 1)"]


def test_require_functions_is_project_wide(rules_challenge):
    """``require_functions`` finds the function in any file of the project."""
    _folder, stages = rules_challenge
    stage_1 = stages[0]
    files = {"commands.py": "x = 1\n", "main.py": COMMANDS}
    result = run_stage_check(stage_1.task, files, stages=[stage_1], timeout=10)
    rows = [tr.description for tr in result.results if tr.description.startswith("Правило")]
    assert rows == []  # ``parse_command`` lives in main.py, still fine


def test_missing_file_of_a_scoped_rule_is_reported(rules_challenge):
    _folder, stages = rules_challenge
    stage_3 = stages[2]
    result = run_stage_check(stage_3.task, {"main.py": ""}, stages=[stage_3], timeout=10)
    assert any("`commands.py` не найден" in tr.description for tr in result.results)


def test_rules_are_not_counted_as_behaviour_checks(rules_challenge):
    """``count_smoke_checks`` (the verifier's smoke budget) skips rule rows."""
    from ego.checker import count_smoke_checks

    _folder, stages = rules_challenge
    files = {"commands.py": COMMANDS, "storage.py": "import json\n"}
    result = run_stage_check(stages[1].task, files, stages=stages[:2], timeout=10)
    rule_rows = [tr for tr in result.results if tr.description.startswith("Правило")]
    assert rule_rows
    assert count_smoke_checks(result) == len(result.results) - len(rule_rows)


# === @rules(file=...) declarations ===


def test_scoped_rules_require_a_project_file_name():
    from ego.testing import rules

    with pytest.raises(ValueError, match="file"):
        rules(file="  ")


def test_scoped_rules_are_recorded_per_file():
    from ego.testing import rules

    @rules(file="storage.py", forbid_imports=["os"])
    def task_scoped(): ...

    assert task_scoped._ego_rules.forbid_imports == ("os",)
    assert set(task_scoped._ego_rules_files) == {"storage.py"}


# === single-file checks are unchanged ===


def test_single_file_check_has_no_stage_fields(tmp_path):
    """``run_check`` never tags a stage: existing tasks behave exactly as before."""
    from ego.checker import run_check

    folder = tmp_path / "task"
    folder.mkdir()
    (folder / "task_t.md").write_text(
        "# Задача T1: T\n## Условие\n\n## Пример\n", encoding="utf-8"
    )
    (folder / "task_t.solution.py").write_text(
        "def task_t(x):\n    return x + 1\n", encoding="utf-8"
    )
    (folder / "task_t.tests.py").write_text(
        "from ego.testing import case\n\n"
        "@case(args=(1,), expected=2, description='плюс один')\n"
        "def task_t(x):\n    ...\n",
        encoding="utf-8",
    )
    result = run_check(
        parse_task_file(folder / "task_t.md"), "def task_t(x):\n    return x + 1\n"
    )
    assert result.all_passed
    for tr in result.results:
        assert tr.stage is None and tr.stage_title == ""


@pytest.fixture(scope="module", autouse=True)
def _no_bytecode():
    """Keep ``__pycache__`` out of the fixture catalog (checked by git)."""
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    yield
    sys.dont_write_bytecode = previous
    for cache in FIXTURE_CATALOG.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)
