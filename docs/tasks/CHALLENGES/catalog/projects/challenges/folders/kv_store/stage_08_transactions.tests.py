"""Этап 8: транзакции MULTI / EXEC / DISCARD (чёрный ящик)."""

from ego.testing import program


@program(
    stdin="MULTI\nSET a 1\nGET a\nEXEC\nEXIT\n",
    expected_stdout="OK\nQUEUED\nQUEUED\nOK\n1",
    description="MULTI, две команды в очереди, EXEC выполняет их",
)
def task_kv08_exec():
    ...


@program(
    stdin="MULTI\nSET a 1\nDISCARD\nGET a\nEXIT\n",
    expected_stdout="OK\nQUEUED\nOK\n(nil)",
    description="DISCARD выбрасывает очередь: SET не выполнился",
)
def task_kv08_discard():
    ...


@program(
    stdin="EXEC\nEXIT\n",
    expected_stdout="ERR EXEC without MULTI",
    description="EXEC без MULTI",
)
def task_kv08_exec_without_multi():
    ...


@program(
    stdin="DISCARD\nEXIT\n",
    expected_stdout="ERR DISCARD without MULTI",
    description="DISCARD без MULTI",
)
def task_kv08_discard_without_multi():
    ...


@program(
    stdin="MULTI\nSET a 1\nEXEC\nGET a\nEXEC\nEXIT\n",
    expected_stdout="OK\nQUEUED\nOK\n1\nERR EXEC without MULTI",
    description="после EXEC команды снова выполняются сразу",
    level="full",
)
def task_kv08_after_exec():
    ...


@program(
    stdin="MULTI\nEXEC\nEXIT\n",
    expected_stdout="OK\n(empty)",
    description="EXEC пустой очереди отвечает (empty)",
    level="full",
)
def task_kv08_empty_exec():
    ...


@program(
    stdin="MULTI\nINCR n\nINCR n\nGET n\nEXEC\nEXIT\n",
    expected_stdout="OK\nQUEUED\nQUEUED\nQUEUED\n1\n2\n2",
    description="EXEC печатает ответ каждой команды на своей строке",
    level="full",
)
def task_kv08_exec_many():
    ...


@program(
    stdin="MULTI\nFOO\nSET a 1\nEXEC\nGET a\nEXIT\n",
    expected_stdout="OK\nQUEUED\nQUEUED\nERR unknown command 'FOO'\nOK\n1",
    description="ошибка внутри транзакции печатается при EXEC, остальное выполняется",
    level="full",
)
def task_kv08_error_inside():
    ...


@program(
    stdin="MULTI\nMULTI\nSET a 1\nEXEC\nEXIT\n",
    expected_stdout="OK\nERR MULTI calls can not be nested\nQUEUED\nOK",
    description="второй MULTI подряд — ошибка, очередь живёт дальше",
    level="full",
)
def task_kv08_nested():
    ...


@program(
    stdin="MULTI\nSET a 1\nDISCARD\nDISCARD\nEXIT\n",
    expected_stdout="OK\nQUEUED\nOK\nERR DISCARD without MULTI",
    description="после DISCARD транзакции нет",
    level="full",
)
def task_kv08_discard_twice():
    ...


@program(
    stdin="SET a 1\nMULTI\nDEL a\nEXISTS a\nEXEC\nEXISTS a\nEXIT\n",
    expected_stdout="OK\nOK\nQUEUED\nQUEUED\n1\n0\n0",
    description="внутри транзакции команды работают с общим хранилищем",
    level="full",
)
def task_kv08_shared_store():
    ...
