"""Этап 5: ошибки приходят текстом (импорт и чёрный ящик)."""

from ego.testing import case, program


@case(
    target="storage.execute",
    args=({}, "FOO", []),
    expected="ERR unknown command 'FOO'",
    description="неизвестная команда",
)
def task_kv05_unknown():
    ...


@case(
    target="storage.execute",
    args=({}, "SET", ["a"]),
    expected="ERR wrong number of arguments for 'SET'",
    description="SET с одним аргументом вместо двух",
)
def task_kv05_set_one_arg():
    ...


@case(
    target="storage.execute",
    args=({}, "GET", []),
    expected="ERR wrong number of arguments for 'GET'",
    description="GET без аргументов",
)
def task_kv05_get_no_args():
    ...


@program(
    stdin="foo bar\nEXIT\n",
    expected_stdout="ERR unknown command 'FOO'",
    description="в программе: неизвестная команда не роняет её",
)
def task_kv05_program_unknown():
    ...


@program(
    stdin="SET a\nGET a\nEXIT\n",
    expected_stdout="ERR wrong number of arguments for 'SET'\n(nil)",
    description="неверный SET ничего не записывает, программа живёт дальше",
)
def task_kv05_program_arity():
    ...


@case(
    target="storage.execute",
    args=({"a": "1"}, "KEYS", ["extra"]),
    expected="ERR wrong number of arguments for 'KEYS'",
    description="KEYS не принимает аргументов",
    level="full",
)
def task_kv05_keys_extra():
    ...


@case(
    target="storage.execute",
    args=({}, "SET", ["a", "1", "2"]),
    expected="ERR wrong number of arguments for 'SET'",
    description="SET с тремя аргументами",
    level="full",
)
def task_kv05_set_three_args():
    ...


@case(
    target="storage.execute",
    args=({}, "DEL", []),
    expected="ERR wrong number of arguments for 'DEL'",
    description="DEL без аргументов",
    level="full",
)
def task_kv05_del_no_args():
    ...


@case(
    target="storage.execute",
    args=({}, "HELLO", ["x"]),
    expected="ERR unknown command 'HELLO'",
    description="неизвестная команда с аргументами",
    level="full",
)
def task_kv05_unknown_args():
    ...


@case(
    target="storage.execute",
    args=({}, "SET", ["a", "1"]),
    expected="OK",
    description="правильная команда работает как раньше",
    level="full",
)
def task_kv05_still_works():
    ...


@program(
    stdin="GET\nDEL\nEXISTS a b\nBAR 1 2\nSET k v\nGET k\nEXIT\n",
    expected_stdout=(
        "ERR wrong number of arguments for 'GET'\n"
        "ERR wrong number of arguments for 'DEL'\n"
        "ERR wrong number of arguments for 'EXISTS'\n"
        "ERR unknown command 'BAR'\n"
        "OK\n"
        "v"
    ),
    description="много ошибок подряд, программа не падает",
    level="full",
)
def task_kv05_many_errors():
    ...
