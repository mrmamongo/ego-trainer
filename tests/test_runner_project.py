"""``run_project`` / ``validate_project_files`` — multi-file sandbox (ADR-0018 D18.4).

Two run shapes: ``target="module.func"`` imports a module of the project and
compares the call's ``repr`` (same comparison and observations as
:func:`ego.runner.run_function`), ``entry="main.py"`` runs the project as a
program with ``stdin`` and compares stdout / exit code / files on disk.
"""

from __future__ import annotations

import pytest

from ego.errors import SandboxError
from ego.runner import parse_return_value, run_code, run_project, validate_project_files

COMMANDS = """\
def parse_command(line):
    parts = line.split()
    if not parts:
        return "EXIT", None
    return parts[0].upper(), parts[1:] or None
"""

MAIN = """\
import json
import os
import sys

from commands import parse_command


def main():
    store = {}
    for line in sys.stdin:
        command, args = parse_command(line.strip())
        if command == "EXIT":
            break
        if command == "SET":
            store[args[0]] = args[1]
            print("OK")
        elif command == "GET":
            print(store.get(args[0], "NONE"))
    os.makedirs("data", exist_ok=True)
    with open("data/store.json", "w", encoding="utf-8") as handle:
        json.dump(store, handle)


if __name__ == "__main__":
    main()
"""


def _project(**extra: str) -> dict[str, str]:
    files = {"commands.py": COMMANDS, "main.py": MAIN}
    files.update(extra)
    return files


# === validate_project_files ===


def test_valid_project_has_no_errors():
    assert validate_project_files(_project()) == []


@pytest.mark.parametrize(
    ("path", "fragment"),
    [
        ("../hack.py", "`..` запрещён"),
        ("/etc/passwd", "абсолютный"),
        ("C:/x.py", "абсолютный"),
        ("pkg\\file.py", "через `/`"),
        ("__pycache__/x.py", "`__pycache__/`"),
        (".cogito/state.json", "`.cogito/`"),
        ("a//b.py", "лишние"),
        ("notes.txt", "не входит в проект"),
    ],
)
def test_bad_paths_are_rejected_in_russian(path, fragment):
    errors = validate_project_files({"main.py": "", path: "x"})
    assert len(errors) == 1
    assert fragment in errors[0]


def test_include_decides_which_files_belong_to_the_project():
    files = {"main.py": "x", "data/store.json": "{}"}
    assert "data/store.json" in validate_project_files(files, {"include": ["*.py"]})[0]
    assert validate_project_files(files, {"include": ["*.py", "data/*.json"]}) == []


def test_max_files_is_enforced():
    files = {f"m{index}.py": "" for index in range(3)}
    assert validate_project_files(files, {"max_files": 3}) == []
    assert "лимита 2" in validate_project_files(files, {"max_files": 2})[0]


def test_max_bytes_is_enforced():
    files = {"main.py": "x" * 50}
    assert validate_project_files(files, {"max_bytes": 50}) == []
    assert "байт" in validate_project_files(files, {"max_bytes": 10})[0]


def test_not_a_dict_is_reported():
    assert validate_project_files(["main.py"])  # type: ignore[list-item]


def test_run_project_raises_on_invalid_files():
    with pytest.raises(SandboxError) as error:
        run_project({"../x.py": ""})
    assert "`..` запрещён" in error.value.message


# === target mode ===


def test_target_calls_module_function():
    result = run_project(_project(), target="commands.parse_command", args=("set a 1",))
    assert result.returncode == 0
    assert parse_return_value(result.stdout) == "('SET', ['a', '1'])"


def test_target_does_not_start_the_entrypoint():
    """Importing the module must not run its ``__main__`` block."""
    result = run_project(_project(), target="main.parse_command", args=("get",))
    assert result.returncode == 0
    assert parse_return_value(result.stdout) == "('GET', None)"


def test_target_sees_project_packages():
    files = {
        "app/__init__.py": "",
        "app/calc.py": "def add(a, b):\n    return a + b\n",
        "app/main.py": "from .calc import add\n\ndef run():\n    return add(2, 3)\n",
    }
    result = run_project(files, target="app.main.run")
    assert parse_return_value(result.stdout) == "5"


def test_target_exception_is_reported():
    result = run_project({"m.py": "def f():\n    raise ValueError('boom')\n"}, target="m.f")
    assert result.returncode != 0
    assert result.exception is not None
    assert "ValueError: boom" in result.stderr


def test_target_missing_module_is_an_error():
    result = run_project({"m.py": ""}, target="nope.f")
    assert result.returncode != 0
    assert "ModuleNotFoundError" in result.stderr


def test_target_value_comparison_and_inputs():
    files = {"m.py": "def f(arg):\n    return arg\n"}
    result = run_project(
        files,
        target="m.f",
        args=({"a": 1},),
        check_inputs_unchanged=True,
        kwargs={},
    )
    assert result.returncode == 0


def test_args_are_literals_not_code():
    """``args`` go through the same ``repr`` path as ``run_function``."""
    result = run_project({"m.py": "def f(x):\n    return x\n"}, target="m.f", args=({"a": 1},))
    assert parse_return_value(result.stdout) == "{'a': 1}"


def test_blocked_imports_still_apply():
    result = run_project({"m.py": "import asyncio\n\ndef f():\n    return 1\n"}, target="m.f")
    assert "WARNING: blocked import: asyncio" in result.stderr
    assert result.blocked_import == "asyncio"


def test_wrapper_imports_are_not_the_students():
    """The wrapper's own ``importlib``/``traceback`` must not be reported."""
    result = run_project({"m.py": "def f():\n    raise RuntimeError('x')\n"}, target="m.f")
    assert result.exception is not None
    assert "blocked import" not in result.stderr


def test_timeout_is_reported():
    result = run_project(
        {"m.py": "def f():\n    while True:\n        pass\n"}, target="m.f", timeout=0.5
    )
    assert result.timed_out


def test_invalid_target_is_rejected():
    with pytest.raises(SandboxError):
        run_project({"m.py": ""}, target="not a target")


# === entry mode ===


def test_entry_runs_program_with_stdin():
    result = run_project(
        _project(),
        entry="main.py",
        stdin="SET a 1\nGET a\nGET b\nEXIT\n",
        expected_stdout="OK\n1\nNONE\n",
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == ["OK", "1", "NONE"]


def test_entry_stdout_mismatch_fails_with_actual_output():
    result = run_project(
        _project(), entry="main.py", stdin="EXIT\n", expected_stdout="OK"
    )
    assert result.returncode != 0
    assert "stdout mismatch" in result.stderr
    assert "--- actual ---" in result.stderr


@pytest.mark.parametrize(
    ("match", "expected", "ok"),
    [
        ("exact", "OK \n\n", True),
        ("exact", " OK \n", False),
        ("lines", "  OK  \n\n", True),
        ("lines", "OK\nNONE", False),
        ("contains", "OK", True),
        ("contains", "OK\nNONE", False),
    ],
)
def test_match_modes(match, expected, ok):
    result = run_project(
        _project(),
        entry="main.py",
        stdin="SET a 1\nEXIT\n",
        expected_stdout=expected,
        match=match,
    )
    assert (result.returncode == 0) is ok, result.stderr


def test_expected_exit_code():
    files = {"main.py": "import sys\nprint('bye')\nsys.exit(3)\n"}
    fine = run_project(
        files, entry="main.py", expected_stdout="bye", expected_exit=3
    )
    assert fine.returncode == 3, fine.stderr
    wrong = run_project(files, entry="main.py", expected_stdout="bye", expected_exit=0)
    assert wrong.returncode == 1
    assert "expected 0" in wrong.stderr


def test_empty_expected_stdout_checks_nothing():
    """``@program(expected_stdout="")`` turns the stdout check off (D18.3)."""
    files = {"main.py": "print('anything')\n"}
    assert run_project(files, entry="main.py").returncode == 0


def test_expect_files_reads_json():
    files = _project()
    result = run_project(
        files,
        entry="main.py",
        stdin="SET a 1\nEXIT\n",
        expected_stdout="OK\n",
        expect_files={"data/store.json": {"a": "1"}},
    )
    assert result.returncode == 0, result.stderr
    assert result.files["data/store.json"] == ({"a": "1"}, "")


def test_expect_files_mismatch_names_the_difference():
    result = run_project(
        _project(),
        entry="main.py",
        stdin="SET a 1\nEXIT\n",
        expect_files={"data/store.json": {"a": "2"}},
    )
    assert result.returncode == 1
    assert "`data/store.json`" in result.stderr
    assert 'ожидалось {"a": "2"}, получено {"a": "1"}' in result.stderr


@pytest.mark.parametrize(
    ("expected", "ok"),
    [
        ({"a": 1}, True),  # number order in a file does not matter
        ({"a": True}, False),  # but True is not 1
        ({"a": 2}, False),
    ],
)
def test_expect_files_json_equality(expected, ok):
    files = {"main.py": "open('out.json', 'w').write('{\"a\": 1.0}')\n"}
    result = run_project(files, entry="main.py", expect_files={"out.json": expected})
    assert (result.returncode == 0) is ok


def test_expect_files_missing_or_not_json():
    files = {
        "main.py": (
            "from pathlib import Path\n"
            "Path('notes.txt').write_text('hello', encoding='utf-8')\n"
            "print('ok')\n"
        )
    }
    result = run_project(
        files,
        entry="main.py",
        expect_files={"data/other.json": {}, "notes.txt": "hello"},
    )
    assert result.returncode == 1
    assert "файл не создан" in result.stderr
    assert "это не JSON" in result.stderr


def test_expect_files_rejects_escaping_path():
    result = run_project(
        _project(), entry="main.py", stdin="EXIT\n", expect_files={"../x.json": {}}
    )
    assert "`..` запрещён" in result.files["../x.json"][1]


def test_missing_entry_file_is_an_error_result():
    result = run_project({"main.py": ""}, entry="other.py")
    assert result.returncode == -1
    assert "не найден" in result.stderr


def test_default_entry_comes_from_workspace():
    result = run_project({"run.py": "print('ok')\n"}, workspace={"entry": "run.py"})
    assert result.stdout.strip() == "ok"


def test_target_and_entry_are_mutually_exclusive():
    # Both may be given; ``target`` wins and ``entry`` is ignored (D18.4).
    result = run_project({"m.py": "def f():\n    return 1\n"}, target="m.f", entry="m.py")
    assert parse_return_value(result.stdout) == "1"


def test_entry_runs_without_site_packages():
    """``python -S``: no ``site`` import, so nothing leaks from the parent."""
    result = run_project(
        {"main.py": "import sys\nprint('site' in sys.modules)\n"}, entry="main.py"
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "False"


def test_run_code_still_works_alongside():
    assert run_code("print(1)").stdout.strip() == "1"
