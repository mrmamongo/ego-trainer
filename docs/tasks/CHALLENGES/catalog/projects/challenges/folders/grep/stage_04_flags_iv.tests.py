"""Этап 4: флаги -i и -v (чёрный ящик)."""

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
    argv=["-i", "error", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_stdout="ERROR disk full\nerror: timeout\nERROR disk full again",
    match="exact",
    expected_exit=0,
    description="-i: большие и маленькие буквы не различаются",
)
def task_gr04_ignore_case():
    ...


@program(
    argv=["-v", "INFO", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_stdout="ERROR disk full\nerror: timeout\nWARN slow response\nERROR disk full again",
    match="exact",
    expected_exit=0,
    description="-v: строки, в которых шаблона нет",
)
def task_gr04_invert():
    ...


@program(
    argv=["-i", "-v", "error", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_stdout="INFO server started\nINFO retry in 5s\nWARN slow response\nINFO done",
    match="exact",
    expected_exit=0,
    description="-i и -v вместе",
)
def task_gr04_both():
    ...


@program(
    argv=["-v", "-i", "INFO", "logs/app.log"],
    files={"logs/app.log": LOG},
    expected_stdout="ERROR disk full\nerror: timeout\nWARN slow response\nERROR disk full again",
    match="exact",
    expected_exit=0,
    description="порядок флагов не важен (-v -i)",
    level="full",
)
def task_gr04_order():
    ...


@program(
    argv=["-v", "o", "words.txt"],
    files={"words.txt": "one\ntwo\nfour\n"},
    expected_exit=1,
    description="-v: все строки подошли под шаблон, выбирать нечего — код 1",
    level="full",
)
def task_gr04_invert_exit_one():
    ...


@program(
    argv=["-v", "zzz", "words.txt"],
    files={"words.txt": "one\ntwo\n"},
    expected_stdout="one\ntwo",
    match="exact",
    expected_exit=0,
    description="-v: шаблона нет нигде — печатаются все строки",
    level="full",
)
def task_gr04_invert_all():
    ...


@program(
    argv=["-i", "HELLO", "words.txt"],
    files={"words.txt": "Hello\nhello\nhELLo!\nbye\n"},
    expected_stdout="Hello\nhello\nhELLo!",
    match="exact",
    expected_exit=0,
    description="-i: строки печатаются как в файле, а не маленькими буквами",
    level="full",
)
def task_gr04_keeps_original():
    ...


@program(
    argv=["-i", "nothing", "words.txt"],
    files={"words.txt": "one\ntwo\n"},
    expected_exit=1,
    description="-i без совпадений: код 1",
    level="full",
)
def task_gr04_ignore_case_exit_one():
    ...


@program(
    argv=["-x", "one", "words.txt"],
    files={"words.txt": "one\n"},
    expected_exit=2,
    expected_stderr="grep:",
    description="неизвестный флаг: сообщение «grep: …» в stderr, код 2",
    level="full",
)
def task_gr04_unknown_flag():
    ...


@program(
    argv=["-i", "error"],
    expected_exit=2,
    expected_stderr="использование:",
    description="флаги есть, а файла нет: использование и код 2",
    level="full",
)
def task_gr04_flags_without_file():
    ...


@program(
    argv=["-v", "x", "nope.txt"],
    expected_exit=2,
    expected_stderr="grep: nope.txt: нет такого файла",
    description="файла нет и с флагами",
    level="full",
)
def task_gr04_missing_with_flags():
    ...
