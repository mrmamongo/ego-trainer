from ego.testing import case, rules

@case(
    args=("привет",),
    expected="Привет",
    description="обычное слово",
    level="smoke",
)

@case(
    args=("a",),
    expected="A",
    description="одна буква",
    level="smoke",
)

@case(
    args=("hello world",),
    expected="Hello world",
    description="две части, остальное не трогаем",
    level="smoke",
)

@case(
    args=("",),
    expected="",
    description="пустая строка",
    level="full",
)

@case(
    args=("мИР",),
    expected="МИР",
    description="остальные заглавные остаются",
    level="full",
)

@case(
    args=("123abc",),
    expected="123abc",
    description="первый символ не буква",
    level="full",
)

@case(
    args=("Кот",),
    expected="Кот",
    description="уже с заглавной",
    level="full",
)


@rules(forbid_methods=["capitalize", "title"])

def task_s06_upper_first(text):
    ...
