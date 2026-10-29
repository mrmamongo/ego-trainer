"""Tests for stage 1 — import mode with ``target=`` (ADR-0018 D18.3)."""

from ego.testing import case, rules


@rules(require_functions=["parse_command"])
@case(
    target="commands.parse_command",
    args=("set a 1",),
    expected=("SET", ["a", "1"]),
    description="SET с аргументами",
)
def task_kv01_parse():
    ...


@case(
    target="commands.parse_command",
    args=("get",),
    expected=("GET", None),
    description="команда без аргументов",
)
def task_kv01_parse_no_args():
    ...


@case(
    target="commands.parse_command",
    args=("  ",),
    expected=("EXIT", None),
    description="строка из пробелов — EXIT",
)
def task_kv01_parse_blank():
    ...


@case(
    target="commands.parse_command",
    args=("",),
    expected=("EXIT", None),
    description="пустая строка — EXIT",
    level="full",
)
def task_kv01_parse_empty():
    ...
