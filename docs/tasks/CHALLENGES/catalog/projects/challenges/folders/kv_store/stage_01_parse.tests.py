"""Этап 1: разбор команды (импорт commands.parse_command)."""

from ego.testing import case, rules


@rules(
    require_functions=["parse_command"],
    forbid_nodes=["ClassDef"],
    messages={"ClassDef": "В этом челлендже классы не нужны: хватит функций, словарей и модулей"},
)
@case(
    target="commands.parse_command",
    args=("set a 1",),
    expected=("SET", ["a", "1"]),
    description="команда и два аргумента",
)
def task_kv01_parse():
    ...


@case(
    target="commands.parse_command",
    args=("GET a",),
    expected=("GET", ["a"]),
    description="команда и один аргумент",
)
def task_kv01_one_arg():
    ...


@case(
    target="commands.parse_command",
    args=("  keys  ",),
    expected=("KEYS", []),
    description="команда без аргументов, пробелы по краям",
)
def task_kv01_no_args():
    ...


@case(
    target="commands.parse_command",
    args=("",),
    expected=("", []),
    description="пустая строка",
    level="full",
)
def task_kv01_empty():
    ...


@case(
    target="commands.parse_command",
    args=("   ",),
    expected=("", []),
    description="строка из одних пробелов",
    level="full",
)
def task_kv01_blank():
    ...


@case(
    target="commands.parse_command",
    args=("  Set    name   Anna   ",),
    expected=("SET", ["name", "Anna"]),
    description="лишние пробелы внутри и по краям",
    level="full",
)
def task_kv01_spaces():
    ...


@case(
    target="commands.parse_command",
    args=("sEt Key Value",),
    expected=("SET", ["Key", "Value"]),
    description="заглавными только имя команды, аргументы не меняются",
    level="full",
)
def task_kv01_case():
    ...
