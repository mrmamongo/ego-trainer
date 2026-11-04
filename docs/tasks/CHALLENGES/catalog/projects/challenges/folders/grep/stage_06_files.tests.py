"""Этап 6: несколько файлов (чёрный ящик)."""

from ego.testing import program

A = "apple pie\nbanana\napple tart\n"
B = "cherry\napple juice\n"
C = "grape\nlemon\n"


@program(
    argv=["apple", "a.txt", "b.txt"],
    files={"a.txt": A, "b.txt": B},
    expected_stdout="a.txt:apple pie\na.txt:apple tart\nb.txt:apple juice",
    match="exact",
    expected_exit=0,
    description="два файла: перед каждой строкой имя файла и двоеточие",
)
def task_gr06_two_files():
    ...


@program(
    argv=["apple", "b.txt", "a.txt"],
    files={"a.txt": A, "b.txt": B},
    expected_stdout="b.txt:apple juice\na.txt:apple pie\na.txt:apple tart",
    match="exact",
    expected_exit=0,
    description="файлы идут в том порядке, в каком названы",
)
def task_gr06_order():
    ...


@program(
    argv=["-c", "apple", "a.txt", "b.txt", "c.txt"],
    files={"a.txt": A, "b.txt": B, "c.txt": C},
    expected_stdout="a.txt:2\nb.txt:1\nc.txt:0",
    match="exact",
    expected_exit=0,
    description="-c: по строке `файл:число` на каждый файл, в том числе 0",
)
def task_gr06_count():
    ...


@program(
    argv=["apple", "a.txt", "nope.txt", "b.txt"],
    files={"a.txt": A, "b.txt": B},
    expected_stdout="a.txt:apple pie\na.txt:apple tart\nb.txt:apple juice",
    match="exact",
    expected_exit=2,
    expected_stderr="grep: nope.txt: нет такого файла",
    description="файл посреди списка не найден: остальные обработаны, код 2",
)
def task_gr06_missing_middle():
    ...


@program(
    argv=["apple", "a.txt"],
    files={"a.txt": A},
    expected_stdout="apple pie\napple tart",
    match="exact",
    expected_exit=0,
    description="один файл: имени файла перед строкой нет (как раньше)",
    level="full",
)
def task_gr06_single_file():
    ...


@program(
    argv=["lemon", "a.txt", "c.txt"],
    files={"a.txt": A, "c.txt": C},
    expected_stdout="c.txt:lemon",
    match="exact",
    expected_exit=0,
    description="совпадение только в одном из файлов",
    level="full",
)
def task_gr06_one_has_matches():
    ...


@program(
    argv=["zzz", "a.txt", "b.txt"],
    files={"a.txt": A, "b.txt": B},
    expected_exit=1,
    description="ни в одном файле ничего нет: код 1",
    level="full",
)
def task_gr06_nothing():
    ...


@program(
    argv=["-n", "apple", "a.txt", "b.txt"],
    files={"a.txt": A, "b.txt": B},
    expected_stdout="a.txt:1:apple pie\na.txt:3:apple tart\nb.txt:2:apple juice",
    match="exact",
    expected_exit=0,
    description="-n с несколькими файлами: `файл:номер:строка`",
    level="full",
)
def task_gr06_numbers():
    ...


@program(
    argv=["x", "n1.txt", "n2.txt"],
    expected_exit=2,
    expected_stderr="grep: n2.txt: нет такого файла",
    description="обоих файлов нет: сообщение про каждый, программа не падает на первом",
    level="full",
)
def task_gr06_all_missing():
    ...


@program(
    argv=["-v", "apple", "a.txt", "b.txt"],
    files={"a.txt": A, "b.txt": B},
    expected_stdout="a.txt:banana\nb.txt:cherry",
    match="exact",
    expected_exit=0,
    description="-v с несколькими файлами",
    level="full",
)
def task_gr06_invert():
    ...


@program(
    argv=["-c", "apple", "a.txt", "nope.txt", "b.txt"],
    files={"a.txt": A, "b.txt": B},
    expected_stdout="a.txt:2\nb.txt:1",
    match="exact",
    expected_exit=2,
    expected_stderr="grep: nope.txt: нет такого файла",
    description="-c: для потерянного файла строки с числом нет",
    level="full",
)
def task_gr06_count_missing():
    ...


@program(
    argv=["-i", "APPLE", "a.txt", "c.txt"],
    files={"a.txt": A, "c.txt": C},
    expected_stdout="a.txt:apple pie\na.txt:apple tart",
    match="exact",
    expected_exit=0,
    description="-i с несколькими файлами",
    level="full",
)
def task_gr06_ignore_case():
    ...


@program(
    argv=["a", "logs/x.log", "y.txt"],
    files={"logs/x.log": "a1\n", "y.txt": "a2\n"},
    expected_stdout="logs/x.log:a1\ny.txt:a2",
    match="exact",
    expected_exit=0,
    description="имя файла печатается так, как оно было в аргументах",
    level="full",
)
def task_gr06_path_as_typed():
    ...
