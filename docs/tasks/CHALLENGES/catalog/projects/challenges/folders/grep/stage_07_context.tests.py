"""Этап 7: контекст -A N / -B N (чёрный ящик)."""

from ego.testing import program

TEXT = (
    "one\n"
    "two\n"
    "TARGET three\n"
    "four\n"
    "five\n"
    "six\n"
    "seven\n"
    "TARGET eight\n"
    "nine\n"
    "ten\n"
)


@program(
    argv=["-A", "1", "TARGET", "f.txt"],
    files={"f.txt": TEXT},
    expected_stdout="TARGET three\nfour\n--\nTARGET eight\nnine",
    match="exact",
    expected_exit=0,
    description="-A 1: строка после каждого совпадения, группы разделены `--`",
)
def task_gr07_after():
    ...


@program(
    argv=["-B", "1", "TARGET", "f.txt"],
    files={"f.txt": TEXT},
    expected_stdout="two\nTARGET three\n--\nseven\nTARGET eight",
    match="exact",
    expected_exit=0,
    description="-B 1: строка перед каждым совпадением",
)
def task_gr07_before():
    ...


@program(
    argv=["-n", "-A", "1", "-B", "1", "TARGET", "f.txt"],
    files={"f.txt": TEXT},
    expected_stdout="2-two\n3:TARGET three\n4-four\n--\n7-seven\n8:TARGET eight\n9-nine",
    match="exact",
    expected_exit=0,
    description="-n и оба флага: у найденных `:`, у соседних `-`",
)
def task_gr07_numbers_both():
    ...


@program(
    argv=["-A", "3", "TARGET", "f.txt"],
    files={"f.txt": TEXT},
    expected_stdout="TARGET three\nfour\nfive\nsix\n--\nTARGET eight\nnine\nten",
    match="exact",
    expected_exit=0,
    description="между группами остаётся пропущенная строка (seven) — нужен `--`",
    level="full",
)
def task_gr07_gap_separator():
    ...


@program(
    argv=["-A", "4", "TARGET", "f.txt"],
    files={"f.txt": TEXT},
    expected_stdout=(
        "TARGET three\nfour\nfive\nsix\nseven\nTARGET eight\nnine\nten"
    ),
    match="exact",
    expected_exit=0,
    description="группы касаются (после six сразу seven): склеиваются без `--`",
    level="full",
)
def task_gr07_touching_groups():
    ...


@program(
    argv=["-B", "5", "TARGET", "f.txt"],
    files={"f.txt": TEXT},
    expected_stdout="one\ntwo\nTARGET three\nfour\nfive\nsix\nseven\nTARGET eight",
    match="exact",
    expected_exit=0,
    description="группы пересекаются: ни одна строка не печатается дважды",
    level="full",
)
def task_gr07_overlap():
    ...


@program(
    argv=["-B", "3", "one", "f.txt"],
    files={"f.txt": TEXT},
    expected_stdout="one",
    match="exact",
    expected_exit=0,
    description="-B у первой строки файла: выше ничего нет",
    level="full",
)
def task_gr07_clamp_start():
    ...


@program(
    argv=["-A", "3", "ten", "f.txt"],
    files={"f.txt": TEXT},
    expected_stdout="ten",
    match="exact",
    expected_exit=0,
    description="-A у последней строки файла: ниже ничего нет",
    level="full",
)
def task_gr07_clamp_end():
    ...


@program(
    argv=["-A", "0", "TARGET", "f.txt"],
    files={"f.txt": TEXT},
    expected_stdout="TARGET three\nTARGET eight",
    match="exact",
    expected_exit=0,
    description="-A 0 то же самое, что без контекста: без `--`",
    level="full",
)
def task_gr07_zero():
    ...


@program(
    argv=["-c", "-A", "2", "TARGET", "f.txt"],
    files={"f.txt": TEXT},
    expected_stdout="2",
    match="exact",
    expected_exit=0,
    description="-c игнорирует контекст",
    level="full",
)
def task_gr07_count():
    ...


@program(
    argv=["-A", "1", "TARGET", "f.txt", "g.txt"],
    files={"f.txt": TEXT, "g.txt": "alpha\nTARGET beta\ngamma\n"},
    expected_stdout=(
        "f.txt:TARGET three\nf.txt-four\n--\nf.txt:TARGET eight\nf.txt-nine\n"
        "--\ng.txt:TARGET beta\ng.txt-gamma"
    ),
    match="exact",
    expected_exit=0,
    description="два файла: `файл:` у найденных, `файл-` у соседних, `--` и между файлами",
    level="full",
)
def task_gr07_two_files():
    ...


@program(
    argv=["-v", "-n", "-A", "1", "b", "h.txt"],
    files={"h.txt": "a\nb\nc\nd\n"},
    expected_stdout="1:a\n2-b\n3:c\n4:d",
    match="exact",
    expected_exit=0,
    description="-v с контекстом: соседом может оказаться строка, которая шаблон содержит",
    level="full",
)
def task_gr07_invert():
    ...


@program(
    argv=["-A", "2", "zzz", "f.txt"],
    files={"f.txt": TEXT},
    expected_exit=1,
    description="с контекстом ничего не найдено: код 1",
    level="full",
)
def task_gr07_nothing():
    ...


@program(
    argv=["-A", "x", "TARGET", "f.txt"],
    files={"f.txt": TEXT},
    expected_exit=2,
    expected_stderr="grep:",
    description="после -A не число: сообщение «grep: …» и код 2",
    level="full",
)
def task_gr07_bad_number():
    ...


@program(
    argv=["-B", "-1", "TARGET", "f.txt"],
    files={"f.txt": TEXT},
    expected_exit=2,
    expected_stderr="grep:",
    description="отрицательное число не годится: код 2",
    level="full",
)
def task_gr07_negative():
    ...


@program(
    argv=["-A", "1", "TARGET", "f.txt", "nope.txt"],
    files={"f.txt": TEXT},
    expected_stdout="f.txt:TARGET three\nf.txt-four\n--\nf.txt:TARGET eight\nf.txt-nine",
    match="exact",
    expected_exit=2,
    expected_stderr="grep: nope.txt: нет такого файла",
    description="контекст и потерянный файл вместе",
    level="full",
)
def task_gr07_missing_file():
    ...
