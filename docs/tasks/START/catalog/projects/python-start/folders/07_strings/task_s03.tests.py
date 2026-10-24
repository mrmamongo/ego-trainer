from ego.testing import case, rules

@case(
    args=("Привет",),
    expected=2,
    description="русские гласные",
    level="smoke",
)

@case(
    args=("Hello World",),
    expected=3,
    description="английские гласные",
    level="smoke",
)

@case(
    args=("ПРИВЕТ",),
    expected=2,
    description="заглавные буквы",
    level="smoke",
)

@case(
    args=("",),
    expected=0,
    description="пустая строка",
    level="full",
)

@case(
    args=("ддд",),
    expected=0,
    description="нет гласных",
    level="full",
)

@case(
    args=("Ёлка и яблоко",),
    expected=6,
    description="ё, я и пробелы",
    level="full",
)

@case(
    args=("AEIOU",),
    expected=5,
    description="все английские заглавные",
    level="full",
)

@case(
    args=("123 !?",),
    expected=0,
    description="цифры и знаки",
    level="full",
)


@rules(forbid_methods=["count"])

def task_s03_count_vowels(text):
    ...
