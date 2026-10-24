from ego.testing import case

@case(
    args=("abc",),
    expected="cba",
    description="три буквы",
    level="smoke",
)

@case(
    args=("Привет",),
    expected="тевирП",
    description="русское слово",
    level="smoke",
)

@case(
    args=("ab cd",),
    expected="dc ba",
    description="пробел внутри",
    level="smoke",
)

@case(
    args=("",),
    expected="",
    description="пустая строка",
    level="full",
)

@case(
    args=("x",),
    expected="x",
    description="один символ",
    level="full",
)

@case(
    args=("12 34",),
    expected="43 21",
    description="цифры",
    level="full",
)
def task_s09_reverse_text(text):
    ...
