"""Этап 6: INCR и DECR (импорт и чёрный ящик)."""

from ego.testing import case, program

# Число хранится текстом: после INCR в словаре лежит "1", а не 1.
INCR_STORED_AS_TEXT = '''\
from storage import execute

store = {}
print(execute(store, "INCR", ["n"]))
print(execute(store, "INCR", ["n"]))
print(execute(store, "DECR", ["n"]))
print(store)
'''

SET_THEN_INCR = '''\
from storage import execute

store = {}
execute(store, "SET", ["n", "9"])
print(execute(store, "INCR", ["n"]))
print(store)
'''


@case(
    target="storage.execute",
    args=({}, "INCR", ["n"]),
    expected="1",
    description="INCR несуществующего ключа начинает с 0",
)
def task_kv06_incr_missing():
    ...


@case(
    target="storage.execute",
    args=({"n": "5"}, "INCR", ["n"]),
    expected="6",
    description="INCR прибавляет единицу",
)
def task_kv06_incr():
    ...


@case(
    target="storage.execute",
    args=({"n": "5"}, "DECR", ["n"]),
    expected="4",
    description="DECR отнимает единицу",
)
def task_kv06_decr():
    ...


@program(
    files={"main.py": INCR_STORED_AS_TEXT},
    expected_stdout="1\n2\n1\n{'n': '1'}",
    description="число в словаре лежит текстом",
)
def task_kv06_text():
    ...


@program(
    stdin="SET n 5\nINCR n\nINCR n\nGET n\nEXIT\n",
    expected_stdout="OK\n6\n7\n7",
    description="в программе: SET, INCR, INCR, GET",
)
def task_kv06_program():
    ...


@case(
    target="storage.execute",
    args=({}, "DECR", ["n"]),
    expected="-1",
    description="DECR несуществующего ключа даёт -1",
    level="full",
)
def task_kv06_decr_missing():
    ...


@case(
    target="storage.execute",
    args=({"n": "-3"}, "INCR", ["n"]),
    expected="-2",
    description="отрицательные числа тоже работают",
    level="full",
)
def task_kv06_negative():
    ...


@case(
    target="storage.execute",
    args=({"name": "Anna"}, "INCR", ["name"]),
    expected="ERR value is not an integer",
    description="INCR текста, который не число",
    level="full",
)
def task_kv06_not_integer():
    ...


@case(
    target="storage.execute",
    args=({"x": "2.5"}, "DECR", ["x"]),
    expected="ERR value is not an integer",
    description="DECR дробного числа",
    level="full",
)
def task_kv06_float_text():
    ...


@case(
    target="storage.execute",
    args=({}, "INCR", []),
    expected="ERR wrong number of arguments for 'INCR'",
    description="INCR без аргументов",
    level="full",
)
def task_kv06_arity():
    ...


@program(
    files={"main.py": SET_THEN_INCR},
    expected_stdout="10\n{'n': '10'}",
    description="после INCR число снова текст",
    level="full",
)
def task_kv06_set_then_incr():
    ...


@program(
    stdin="SET name Anna\nINCR name\nGET name\nEXIT\n",
    expected_stdout="OK\nERR value is not an integer\nAnna",
    description="после ошибки значение не меняется",
    level="full",
)
def task_kv06_error_keeps_value():
    ...


@program(
    stdin="INCR hits\nINCR hits\nDECR hits\nDECR hits\nDECR hits\nGET hits\nEXIT\n",
    expected_stdout="1\n2\n1\n0\n-1\n-1",
    description="счётчик идёт вверх, вниз и ниже нуля",
    level="full",
)
def task_kv06_counter():
    ...
