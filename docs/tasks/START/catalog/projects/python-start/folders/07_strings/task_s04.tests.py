from ego.testing import case

@case(
    args=("abc1",),
    expected=True,
    description="цифра в конце",
    level="smoke",
)

@case(
    args=("hello",),
    expected=False,
    description="цифр нет",
    level="smoke",
)

@case(
    args=("Дом 5",),
    expected=True,
    description="цифра после пробела",
    level="smoke",
)

@case(
    args=("",),
    expected=False,
    description="пустая строка",
    level="full",
)

@case(
    args=("7",),
    expected=True,
    description="одна цифра",
    level="full",
)

@case(
    args=("a b-c!",),
    expected=False,
    description="пробелы и знаки без цифр",
    level="full",
)

@case(
    args=("9 а",),
    expected=True,
    description="цифра в начале",
    level="full",
)
def task_s04_has_digit(text):
    ...
