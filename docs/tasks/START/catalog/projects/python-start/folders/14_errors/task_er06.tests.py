from ego.testing import case, rules

@case(
    args=("25",),
    expected=25,
    description='нормальный возраст',
    level="smoke",
)

@case(
    args=("abc",),
    expected=["error", "ValueError", "не число"],
    description='не число',
    level="smoke",
)

@case(
    args=("-3",),
    expected=["error", "ValueError", "меньше нуля"],
    description='отрицательный',
    level="smoke",
)

@case(
    args=("200",),
    expected=["error", "ValueError", "больше 150"],
    description='слишком большой',
    level="smoke",
)

@case(
    args=("0",),
    expected=0,
    description='граница: ноль подходит',
    level="full",
)

@case(
    args=("150",),
    expected=150,
    description='граница: 150 подходит',
    level="full",
)

@case(
    args=("151",),
    expected=["error", "ValueError", "больше 150"],
    description='граница: 151 уже много',
    level="full",
)

@case(
    args=("",),
    expected=["error", "ValueError", "не число"],
    description='пустая строка',
    level="full",
)

@case(
    args=("12.5",),
    expected=["error", "ValueError", "не число"],
    description='дробное не годится',
    level="full",
    hide_expected=True,
)

@case(
    args=(" 40 ",),
    expected=40,
    description='пробелы по краям',
    level="full",
    hide_expected=True,
)


@rules(require_functions=["parse_age"])

def task_er06_age(text):
    ...
