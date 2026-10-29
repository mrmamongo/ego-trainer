"""Этап 3: DEL, EXISTS и KEYS (импорт storage.execute)."""

from ego.testing import case, program

DELETE = '''\
from storage import execute

store = {"a": "1", "b": "2"}
print(execute(store, "DEL", ["a"]))
print(execute(store, "DEL", ["a"]))
print(store)
'''

KEYS_AFTER_DELETE = '''\
from storage import execute

store = {}
execute(store, "SET", ["b", "2"])
execute(store, "SET", ["a", "1"])
execute(store, "DEL", ["b"])
print(execute(store, "KEYS", []))
execute(store, "DEL", ["a"])
print(execute(store, "KEYS", []))
'''


@case(
    target="storage.execute",
    args=({"a": "1"}, "DEL", ["a"]),
    expected="1",
    description="DEL существующего ключа отвечает 1",
)
def task_kv03_del():
    ...


@case(
    target="storage.execute",
    args=({"a": "1"}, "EXISTS", ["a"]),
    expected="1",
    description="EXISTS для ключа, который есть, отвечает 1",
)
def task_kv03_exists():
    ...


@case(
    target="storage.execute",
    args=({"b": "2", "a": "1", "c": "3"}, "KEYS", []),
    expected="a b c",
    description="KEYS: ключи по алфавиту через пробел",
)
def task_kv03_keys():
    ...


@program(
    files={"main.py": DELETE},
    expected_stdout="1\n0\n{'b': '2'}",
    description="DEL убирает ключ из словаря, второй раз отвечает 0",
)
def task_kv03_state():
    ...


@case(
    target="storage.execute",
    args=({"a": "1"}, "DEL", ["zzz"]),
    expected="0",
    description="DEL несуществующего ключа отвечает 0",
    level="full",
)
def task_kv03_del_missing():
    ...


@case(
    target="storage.execute",
    args=({"a": "1"}, "EXISTS", ["b"]),
    expected="0",
    description="EXISTS для ключа, которого нет, отвечает 0",
    level="full",
)
def task_kv03_exists_missing():
    ...


@case(
    target="storage.execute",
    args=({}, "KEYS", []),
    expected="(empty)",
    description="KEYS пустого хранилища отвечает (empty)",
    level="full",
)
def task_kv03_keys_empty():
    ...


@case(
    target="storage.execute",
    args=({"only": "1"}, "KEYS", []),
    expected="only",
    description="KEYS с одним ключом",
    level="full",
)
def task_kv03_keys_one():
    ...


@program(
    files={"main.py": KEYS_AFTER_DELETE},
    expected_stdout="a\n(empty)",
    description="KEYS не показывает удалённые ключи",
    level="full",
)
def task_kv03_keys_after_delete():
    ...
