from ego.testing import case, rules

@case(
    args=("5", -1),
    expected=500,
    description='хороший текст: копейки',
    level="smoke",
)

@case(
    args=("12", 0),
    expected=1200,
    description='другое число',
    level="smoke",
)

@case(
    args=("abc", -1),
    expected=-1,
    description='не число: default',
    level="smoke",
)

@case(
    args=("", 7),
    expected=7,
    description='пустая строка: default',
    level="full",
)

@case(
    args=(" 3 ", 0),
    expected=300,
    description='пробелы по краям',
    level="full",
)

@case(
    args=(None, -1),
    expected=["error", "TypeError", "int() argument must be a string, a bytes-like object or a real number, not 'NoneType'"],
    description='не строка: ошибку нельзя прятать',
    level="full",
    hide_expected=True,
)


@rules(require_functions=["read_cents"])

def task_er04_cents(text, default):
    ...
