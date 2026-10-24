from ego.testing import case

@case(
    args=("  hello   world ",),
    expected="hello world",
    description="пробелы везде",
    level="smoke",
)

@case(
    args=("a  b  c",),
    expected="a b c",
    description="несколько пробелов внутри",
    level="smoke",
)

@case(
    args=("один",),
    expected="один",
    description="уже нормально",
    level="smoke",
)

@case(
    args=("",),
    expected="",
    description="пустая строка",
    level="full",
)

@case(
    args=("   ",),
    expected="",
    description="только пробелы",
    level="full",
)

@case(
    args=(" привет,   мир! ",),
    expected="привет, мир!",
    description="знаки препинания остаются",
    level="full",
)
def task_s15_normalize_spaces(text):
    ...
