from ego.testing import case, rules

@case(
    args=("hello world",),
    expected="Hello World",
    description="два слова",
    level="smoke",
)

@case(
    args=("привет мир",),
    expected="Привет Мир",
    description="русские слова",
    level="smoke",
)

@case(
    args=("мОй дОм",),
    expected="Мой Дом",
    description="регистр вперемешку",
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
    description="одна буква",
    level="full",
)

@case(
    args=("ЕГЭ по физике",),
    expected="Егэ По Физике",
    description="заглавные внутри слова",
    level="full",
)

@case(
    args=("один",),
    expected="Один",
    description="одно слово",
    level="full",
)


@rules(forbid_methods=["title", "capitalize"])

def task_s21_title_case(text):
    ...
