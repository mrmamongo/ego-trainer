"""Этап 3: main.py ШАБЛОН ФАЙЛ (чёрный ящик с аргументами, кодами выхода и stderr)."""

from ego.testing import program

LOG = (
    "INFO server started\n"
    "ERROR disk full\n"
    "INFO retry in 5s\n"
    "error: timeout\n"
    "WARN slow response\n"
    "ERROR disk full again\n"
    "INFO done\n"
)


@program(
    argv=["ERROR", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_stdout="ERROR disk full\nERROR disk full again",
    match="exact",
    expected_exit=0,
    description="печатает подходящие строки, код 0",
)
def task_gr03_found():
    ...


@program(
    argv=["CRITICAL", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_exit=1,
    description="ничего не нашлось: код 1",
)
def task_gr03_nothing():
    ...


@program(
    argv=["ERROR", "logs/missing.log"],
    expected_exit=2,
    expected_stderr="grep: logs/missing.log: нет такого файла",
    description="файла нет: сообщение в stderr и код 2",
)
def task_gr03_missing_file():
    ...


@program(
    argv=["ERROR"],
    expected_exit=2,
    expected_stderr="использование:",
    description="не хватает аргументов: строка «использование:» в stderr, код 2",
)
def task_gr03_usage():
    ...


@program(
    argv=[],
    expected_exit=2,
    expected_stderr="использование:",
    description="совсем без аргументов тоже код 2",
    level="full",
)
def task_gr03_no_args():
    ...


@program(
    argv=["error", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_stdout="error: timeout",
    match="exact",
    expected_exit=0,
    description="большие и маленькие буквы различаются",
    level="full",
)
def task_gr03_case():
    ...


@program(
    argv=["disk full", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_stdout="ERROR disk full\nERROR disk full again",
    match="exact",
    expected_exit=0,
    description="шаблон с пробелом (один аргумент)",
    level="full",
)
def task_gr03_spaces():
    ...


@program(
    argv=["end", "notes.txt"],
    files={"notes.txt": "first\nthe end"},
    expected_stdout="the end",
    match="exact",
    expected_exit=0,
    description="последняя строка файла без перевода строки на конце",
    level="full",
)
def task_gr03_no_final_newline():
    ...


@program(
    argv=["", "notes.txt"],
    files={"notes.txt": "a\n\nb\n"},
    expected_stdout="a\n\nb",
    match="exact",
    expected_exit=0,
    description="пустой шаблон выводит все строки, пустые тоже",
    level="full",
)
def task_gr03_empty_pattern():
    ...

