"""Этап 2: SET и GET (импорт storage.execute)."""

from ego.testing import case, program, rules

# Сам словарь после вызова не виден в @case, поэтому его печатает этот
# маленький «главный файл»: он подменяет main.py только на время проверки.
SET_THEN_GET = '''\
from storage import execute

store = {}
print(execute(store, "SET", ["a", "1"]))
print(execute(store, "GET", ["a"]))
print(store)
'''

OVERWRITE = '''\
from storage import execute

store = {"code": "1"}
print(execute(store, "SET", ["code", "007"]))
print(execute(store, "GET", ["code"]))
print(store)
'''


@rules(require_functions=["execute"])
@case(
    target="storage.execute",
    args=({}, "SET", ["a", "1"]),
    expected="OK",
    description="SET отвечает OK",
)
def task_kv02_set():
    ...


@case(
    target="storage.execute",
    args=({"a": "1"}, "GET", ["a"]),
    expected="1",
    description="GET отдаёт значение",
)
def task_kv02_get():
    ...


@case(
    target="storage.execute",
    args=({"a": "1"}, "GET", ["b"]),
    expected="(nil)",
    description="GET несуществующего ключа отвечает (nil)",
)
def task_kv02_get_missing():
    ...


@program(
    files={"main.py": SET_THEN_GET},
    expected_stdout="OK\n1\n{'a': '1'}",
    description="SET записывает значение в словарь store",
)
def task_kv02_state():
    ...


@case(
    target="storage.execute",
    args=({}, "GET", ["a"]),
    expected="(nil)",
    description="GET из пустого хранилища",
    level="full",
)
def task_kv02_get_empty():
    ...


@case(
    target="storage.execute",
    args=({"x": "5", "y": "7"}, "GET", ["y"]),
    expected="7",
    description="GET берёт именно свой ключ",
    level="full",
)
def task_kv02_get_other():
    ...


@program(
    files={"main.py": OVERWRITE},
    expected_stdout="OK\n007\n{'code': '007'}",
    description="SET заменяет старое значение и хранит его как текст",
    level="full",
)
def task_kv02_overwrite():
    ...
