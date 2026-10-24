from ego.testing import case

@case(
    args=("a1b2-c",),
    expected="abc",
    description="буквы и цифры",
    level="smoke",
)

@case(
    args=("Hello, World!",),
    expected="HelloWorld",
    description="знаки и пробел",
    level="smoke",
)

@case(
    args=("Привет мир",),
    expected="Приветмир",
    description="русские буквы",
    level="smoke",
)

@case(
    args=("",),
    expected="",
    description="пустая строка",
    level="full",
)

@case(
    args=("123",),
    expected="",
    description="ни одной буквы",
    level="full",
)

@case(
    args=("+7(900)",),
    expected="",
    description="телефонные знаки",
    level="full",
)

@case(
    args=("abc",),
    expected="abc",
    description="одни буквы",
    level="full",
)
def task_s05_only_letters(text):
    ...
