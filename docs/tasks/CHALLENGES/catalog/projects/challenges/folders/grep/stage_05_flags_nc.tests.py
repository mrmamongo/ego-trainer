"""Этап 5: флаги -n и -c (чёрный ящик)."""

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
    argv=["-n", "ERROR", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_stdout="2:ERROR disk full\n6:ERROR disk full again",
    match="exact",
    expected_exit=0,
    description="-n: перед строкой номер и двоеточие",
)
def task_gr05_numbers():
    ...


@program(
    argv=["-c", "ERROR", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_stdout="2",
    match="exact",
    expected_exit=0,
    description="-c: печатается только количество",
)
def task_gr05_count():
    ...


@program(
    argv=["-n", "-v", "INFO", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_stdout="2:ERROR disk full\n4:error: timeout\n5:WARN slow response\n6:ERROR disk full again",
    match="exact",
    expected_exit=0,
    description="-n с -v: номера настоящие, из файла",
)
def task_gr05_numbers_invert():
    ...


@program(
    argv=["-c", "-n", "ERROR", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_stdout="2",
    match="exact",
    expected_exit=0,
    description="-c главнее -n: строки не печатаются, только число",
    level="full",
)
def task_gr05_count_wins():
    ...


@program(
    argv=["-c", "CRITICAL", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_stdout="0",
    match="exact",
    expected_exit=1,
    description="-c без совпадений: печатается 0, код 1",
    level="full",
)
def task_gr05_count_zero():
    ...


@program(
    argv=["-i", "-c", "error", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_stdout="3",
    match="exact",
    expected_exit=0,
    description="-i и -c вместе",
    level="full",
)
def task_gr05_count_ignore_case():
    ...


@program(
    argv=["-c", "-v", "INFO", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_stdout="4",
    match="exact",
    expected_exit=0,
    description="-c и -v вместе: считаются строки без шаблона",
    level="full",
)
def task_gr05_count_invert():
    ...


@program(
    argv=["-n", "-i", "WARN", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_stdout="5:WARN slow response",
    match="exact",
    expected_exit=0,
    description="-n и -i вместе",
    level="full",
)
def task_gr05_numbers_ignore_case():
    ...


@program(
    argv=["-n", "x", "words.txt"],
    files={"words.txt": "one\ntwo\n"},
    expected_exit=1,
    description="-n без совпадений: код 1",
    level="full",
)
def task_gr05_numbers_nothing():
    ...


@program(
    argv=["-c", "x", "nope.txt"],
    expected_exit=2,
    expected_stderr="grep: nope.txt: нет такого файла",
    description="-c и файла нет: сообщение и код 2",
    level="full",
)
def task_gr05_count_missing():
    ...


@program(
    argv=["-n", "", "words.txt"],
    files={"words.txt": "a\n\nb\n"},
    expected_stdout="1:a\n2:\n3:b",
    match="exact",
    expected_exit=0,
    description="пустая строка файла тоже получает номер",
    level="full",
)
def task_gr05_blank_line_number():
    ...
