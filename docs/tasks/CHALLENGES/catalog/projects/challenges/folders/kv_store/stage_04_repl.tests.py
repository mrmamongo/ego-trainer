"""Этап 4: цикл команд в main.py (чёрный ящик)."""

from ego.testing import program


@program(
    stdin="SET a 1\nGET a\nEXIT\n",
    expected_stdout="OK\n1",
    description="SET, потом GET, потом EXIT",
)
def task_kv04_set_get():
    ...


@program(
    stdin="SET a 1\nEXIT\nGET a\n",
    expected_stdout="OK",
    description="после EXIT команды больше не читаются",
)
def task_kv04_exit_stops():
    ...


@program(
    stdin="SET x 5\nSET y 6\nKEYS\nDEL x\nEXISTS x\nEXIT\n",
    expected_stdout="OK\nOK\nx y\n1\n0",
    description="несколько разных команд подряд",
)
def task_kv04_session():
    ...


@program(
    stdin="SET a 1\nGET a\n",
    expected_stdout="OK\n1",
    description="ввод закончился без EXIT — программа завершается сама",
)
def task_kv04_eof():
    ...


@program(
    stdin="",
    expected_stdout="",
    match="exact",
    description="пустой ввод — ничего не печатаем",
    level="full",
)
def task_kv04_empty_input():
    ...


@program(
    stdin="\n   \nSET a 1\n\nGET a\nEXIT\n",
    expected_stdout="OK\n1\n",
    match="exact",
    description="пустые строки пропускаются и ничего не печатают",
    level="full",
)
def task_kv04_blank_lines():
    ...


@program(
    stdin="set k hello\nget k\nkeys\nexit\n",
    expected_stdout="OK\nhello\nk",
    description="команды можно писать маленькими буквами, в том числе exit",
    level="full",
)
def task_kv04_lowercase():
    ...


@program(
    stdin="SET a 1\nSET a 2\nGET a\nEXIT\n",
    expected_stdout="OK\nOK\n2",
    description="хранилище живёт между командами",
    level="full",
)
def task_kv04_state():
    ...
