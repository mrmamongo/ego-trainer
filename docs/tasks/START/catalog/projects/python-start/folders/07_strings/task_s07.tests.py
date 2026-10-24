from ego.testing import case, rules

@case(
    args=("привет",),
    expected="Привет",
    description="маленькие буквы",
    level="smoke",
)

@case(
    args=("ПРИВЕТ",),
    expected="Привет",
    description="все заглавные",
    level="smoke",
)

@case(
    args=("мИр",),
    expected="Мир",
    description="вперемешку",
    level="smoke",
)

@case(
    args=("",),
    expected="",
    description="пустая строка",
    level="full",
)

@case(
    args=("a",),
    expected="A",
    description="один символ",
    level="full",
)

@case(
    args=("hELLO wORLD",),
    expected="Hello world",
    description="пробел внутри",
    level="full",
)

@case(
    args=("5Кот",),
    expected="5кот",
    description="первый символ цифра",
    level="full",
)


@rules(forbid_methods=["capitalize", "title"])

def task_s07_capitalize_first(text):
    ...
