"""Tests for stage 2 — black-box runs with ``@program`` (ADR-0018 D18.3)."""

from ego.testing import program


@program(
    stdin="SET b 2\nEXIT\n",
    expected_stdout="OK",
    description="SET печатает OK",
)
def task_kv02_set():
    ...


@program(
    stdin="GET b\nEXIT\n",
    expected_stdout="NONE",
    description="неизвестный ключ печатает NONE",
)
def task_kv02_get_missing():
    ...


@program(
    stdin="SET a 1\nGET a\nEXIT\n",
    expected_stdout="OK\n1\n",
    description="SET, потом GET",
    files={"data/store.json": '{"x": "5"}'},
    expect_files={"data/store.json": {"x": "5", "a": "1"}},
)
def task_kv02_repl():
    ...


@program(
    stdin="EXIT\n",
    expected_stdout="",
    description="пустое хранилище сохраняется",
    expect_files={"data/store.json": {}},
    level="full",
)
def task_kv02_empty():
    ...
