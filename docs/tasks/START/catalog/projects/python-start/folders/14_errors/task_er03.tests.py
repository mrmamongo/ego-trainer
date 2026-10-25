from ego.testing import case, rules

@case(
    args=("42", 0),
    expected=42,
    description='обычное число',
    level="smoke",
)

@case(
    args=("abc", 0),
    expected=0,
    description='не число: вернуть default',
    level="smoke",
)

@case(
    args=("-7", 5),
    expected=-7,
    description='отрицательное число — это число',
    level="smoke",
)

@case(
    args=("", 9),
    expected=9,
    description='пустая строка',
    level="full",
)

@case(
    args=("4.5", -1),
    expected=-1,
    description='дробное не годится для int',
    level="full",
)

@case(
    args=(" 12 ", 0),
    expected=12,
    description='пробелы по краям int терпит',
    level="full",
)

@case(
    args=("007", 1),
    expected=7,
    description='ведущие нули',
    level="full",
)


@rules(
    forbid_methods=["isdigit"],
    messages={"isdigit": "isdigit() не понимает минус: используй try/except ValueError"},
)

def task_er03_safe_int(text, default):
    ...
