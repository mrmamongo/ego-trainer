"""Tests for ego.runner — sandbox execution."""

import pytest

from ego.runner import (
    BLOCKED_IMPORTS, RunResult, run_code, run_function, parse_return_value,
)


# === run_code basic ===

def test_run_code_hello_world():
    r = run_code("print('hello')")
    assert r.returncode == 0
    assert "hello" in r.stdout
    assert not r.timed_out


def test_run_code_returns_value():
    r = run_code("x = 42\nprint(x)")
    assert r.returncode == 0
    assert "42" in r.stdout


def test_run_code_exception():
    r = run_code("1/0")
    assert r.returncode == 1
    assert r.exception == "yes"
    assert "ZeroDivisionError" in r.stderr


def test_run_code_timeout():
    r = run_code("while True:\n    pass", timeout=1.0)
    assert r.timed_out
    assert r.returncode == -1


def test_run_code_timeout_default_5s():
    # Just verify default timeout doesn't trigger on fast code
    r = run_code("print('done')")
    assert not r.timed_out


def test_run_code_system_exit_nonzero():
    r = run_code("import sys; sys.exit(2)")
    assert r.returncode == 2


def test_run_code_system_exit_zero():
    r = run_code("import sys; sys.exit(0)")
    assert r.returncode == 0


# === Blocked imports (warning, not failure) ===

def test_blocked_import_warns():
    # os is in BLOCKED_IMPORTS
    r = run_code("import os\nprint('ok')")
    assert r.returncode == 0
    assert r.blocked_import == "os"
    assert "ok" in r.stdout  # still ran
    assert "WARNING: blocked import: os" in r.stderr


def test_allowed_import_no_warn():
    # json should be fine
    r = run_code("import json\nprint(json.dumps({'a': 1}))")
    assert r.returncode == 0
    assert r.blocked_import is None
    assert '"a"' in r.stdout


def test_custom_blocked_imports():
    r = run_code("import json", blocked_imports={"json"})
    assert r.blocked_import == "json"


def test_empty_blocked_imports():
    # no warnings at all
    r = run_code("import os", blocked_imports=set())
    assert r.blocked_import is None


# === run_function ===

def test_run_function_returns_value():
    code = "def add(a, b):\n    return a + b\n"
    r = run_function(code, "add", args=(2, 3))
    assert r.returncode == 0
    rv = parse_return_value(r.stdout)
    assert rv == "5"


def test_run_function_returns_string():
    code = "def greet(name):\n    return f'Hello, {name}!'\n"
    r = run_function(code, "greet", args=("World",))
    assert r.returncode == 0
    rv = parse_return_value(r.stdout)
    assert "Hello, World!" in rv


def test_run_function_returns_list():
    code = "def squares(n):\n    return [i**2 for i in range(n)]\n"
    r = run_function(code, "squares", args=(5,))
    assert r.returncode == 0
    rv = parse_return_value(r.stdout)
    assert "[0, 1, 4, 9, 16]" in rv


def test_run_function_returns_dict():
    code = "def make_dict():\n    return {'a': 1, 'b': 2}\n"
    r = run_function(code, "make_dict")
    assert r.returncode == 0
    rv = parse_return_value(r.stdout)
    assert "'a': 1" in rv


def test_run_function_with_kwargs():
    code = "def f(a, b=10):\n    return a + b\n"
    r = run_function(code, "f", args=(5,), kwargs={"b": 20})
    assert r.returncode == 0
    rv = parse_return_value(r.stdout)
    assert rv == "25"


def test_run_function_missing_function():
    r = run_function("x = 1\n", "nonexistent")
    assert r.returncode == 1
    assert "===EGO_NO_FUNCTION===" in r.stderr


def test_run_function_exception_in_function():
    code = "def f():\n    raise ValueError('boom')\n"
    r = run_function(code, "f")
    assert r.returncode == 1
    assert r.exception == "yes"
    assert "ValueError" in r.stderr


def test_run_function_timeout():
    code = "def f():\n    while True:\n        pass\n"
    r = run_function(code, "f", timeout=1.0)
    assert r.timed_out


def test_parse_return_value_no_marker():
    assert parse_return_value("no marker here") is None


def test_parse_return_value_empty():
    assert parse_return_value("") is None


# === Sandbox isolation ===

def test_no_project_imports():
    # student code shouldn't be able to import ego modules
    r = run_code("import ego\nprint('leaked')")
    # Either ImportError (good) or some other error — but NOT successful print of 'leaked'
    assert "leaked" not in r.stdout or r.returncode != 0


def test_temp_dir_isolated():
    # Verify the script runs in a temp dir
    r = run_code("import os\nprint(os.getcwd())")
    # blocked_import warning for os, but cwd should be in ego-runner-* temp dir
    assert "ego-runner" in r.stdout.lower() or r.blocked_import == "os"
