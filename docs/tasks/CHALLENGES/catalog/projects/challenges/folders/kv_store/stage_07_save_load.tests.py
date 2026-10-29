"""Этап 7: SAVE и загрузка data/store.json (чёрный ящик с файлами)."""

from ego.testing import program, rules

# Запускает main.py как есть, а потом читает файл как текст и смотрит,
# что русские буквы лежат в нём буквами, а не кодами вида А.
RAW_TEXT_CHECK = '''\
with open("main.py", encoding="utf-8") as handle:
    exec(compile(handle.read(), "main.py", "exec"))

with open("data/store.json", encoding="utf-8") as handle:
    text = handle.read()
print("имя" in text and "Аня" in text)
'''


@rules(forbid_imports=["pickle", "shelve"], messages={"pickle": "Храним в JSON, а не в pickle"})
@program(
    stdin="SET a 1\nSAVE\nEXIT\n",
    expected_stdout="OK\nOK",
    expect_files={"data/store.json": {"a": "1"}},
    description="SAVE создаёт data/store.json (папки data сначала нет)",
)
def task_kv07_save():
    ...


@program(
    stdin="GET x\nEXIT\n",
    expected_stdout="5",
    files={"data/store.json": '{"x": "5"}'},
    description="при старте хранилище читается из data/store.json",
)
def task_kv07_load():
    ...


@program(
    stdin="GET x\nEXIT\n",
    expected_stdout="(nil)",
    description="файла нет — хранилище просто пустое, программа не падает",
)
def task_kv07_no_file():
    ...


@program(
    stdin="SET a 1\nSAVE\nEXIT\n",
    expected_stdout="OK\nOK",
    files={"data/store.json": '{"x": "5"}'},
    expect_files={"data/store.json": {"x": "5", "a": "1"}},
    description="загруженные ключи сохраняются вместе с новыми",
)
def task_kv07_load_and_save():
    ...


@program(
    stdin="SET a 1\nEXIT\n",
    expected_stdout="OK",
    files={"data/store.json": '{"x": "5"}'},
    expect_files={"data/store.json": {"x": "5"}},
    description="без SAVE файл не меняется",
    level="full",
)
def task_kv07_no_auto_save():
    ...


@program(
    stdin="SAVE\nEXIT\n",
    expected_stdout="OK",
    expect_files={"data/store.json": {}},
    description="пустое хранилище тоже сохраняется",
    level="full",
)
def task_kv07_save_empty():
    ...


@program(
    stdin="DEL x\nSAVE\nEXIT\n",
    expected_stdout="1\nOK",
    files={"data/store.json": '{"x": "5", "y": "6"}'},
    expect_files={"data/store.json": {"y": "6"}},
    description="удалённый ключ пропадает из файла",
    level="full",
)
def task_kv07_save_after_del():
    ...


@program(
    stdin="INCR n\nINCR n\nSAVE\nEXIT\n",
    expected_stdout="1\n2\nOK",
    expect_files={"data/store.json": {"n": "2"}},
    description="числа сохраняются текстом",
    level="full",
)
def task_kv07_save_numbers():
    ...


@program(
    stdin="SET имя Аня\nSAVE\nGET имя\nEXIT\n",
    expected_stdout="OK\nOK\nАня",
    expect_files={"data/store.json": {"имя": "Аня"}},
    description="русские буквы сохраняются и читаются",
    level="full",
)
def task_kv07_unicode():
    ...


@program(
    entry="check_raw_text.py",
    files={"check_raw_text.py": RAW_TEXT_CHECK},
    stdin="SET имя Аня\nSAVE\nEXIT\n",
    expected_stdout="OK\nOK\nTrue",
    description="в файле буквы остались буквами: ensure_ascii=False",
    level="full",
)
def task_kv07_ensure_ascii():
    ...
