"""``@program(argv=..., expected_stderr=...)`` for command-line challenge stages."""

from __future__ import annotations

import pytest

from ego.checker import ProgramTest, _run_program
from ego.runner import run_project
from ego.testing import ProgramCase, program

ECHO = (
    "import sys\n"
    "print(' '.join(sys.argv[1:]))\n"
    "if len(sys.argv) < 2:\n"
    "    print('usage: main.py WORD', file=sys.stderr)\n"
    "    sys.exit(2)\n"
)


def test_program_decorator_stores_argv_and_expected_stderr():
    @program(argv=["-i", "error"], expected_stderr="usage", expected_exit=2)
    def stage(): ...

    (case,) = stage._ego_programs
    assert case.argv == ("-i", "error")
    assert case.expected_stderr == "usage"


@pytest.mark.parametrize("bad", ["-i error", b"x", [1], ("a", None), 5])
def test_program_rejects_bad_argv(bad):
    with pytest.raises(ValueError, match="argv"):
        program(argv=bad)


def test_program_rejects_non_string_expected_stderr():
    with pytest.raises(ValueError, match="expected_stderr"):
        program(expected_stderr=3)  # type: ignore[arg-type]


def test_run_project_passes_argv_to_the_entry():
    result = run_project({"main.py": ECHO}, entry="main.py", argv=["a", "b c"], expected_stdout="a b c")
    assert result.returncode == 0, result.stderr
    assert result.failure is None


def test_run_project_expected_stderr_is_a_contains_check():
    files = {"main.py": ECHO}
    ok = run_project(files, entry="main.py", expected_exit=2, expected_stderr="usage: main.py")
    assert ok.failure is None and ok.returncode == 2
    bad = run_project(files, entry="main.py", expected_exit=2, expected_stderr="нет такого файла")
    assert bad.failure and "stderr mismatch" in bad.failure


def _check(case: ProgramCase, files: dict[str, str]):
    return _run_program(ProgramTest(program=case), files, workspace=None, timeout=5.0)


def test_checker_accepts_a_nonzero_exit_that_was_expected():
    files = {"main.py": ECHO}
    case = ProgramCase(expected_exit=2, expected_stderr="usage")
    assert _check(case, files).passed
    assert not _check(ProgramCase(expected_exit=1), files).passed
    assert not _check(ProgramCase(), files).passed  # exit 2 where 0 is expected


def test_checker_reports_stderr_mismatch():
    result = _check(ProgramCase(expected_exit=2, expected_stderr="grep:"), {"main.py": ECHO})
    assert not result.passed
    assert "stderr mismatch" in result.error


def test_case_files_outside_include_reach_the_sandbox():
    """``files=`` of a case (``logs/app.log``) are laid out though ``*.py`` is the only include."""
    main = "import sys\nwith open(sys.argv[1]) as f:\n    print(f.read().strip())\n"
    case = ProgramCase(
        argv=("logs/app.log",),
        expected_stdout="hello",
        files={"logs/app.log": "hello\n"},
    )
    assert _check(case, {"main.py": main}).passed
