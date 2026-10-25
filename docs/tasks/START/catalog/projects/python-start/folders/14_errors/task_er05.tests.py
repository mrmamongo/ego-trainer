from ego.testing import case, rules

@case(
    args=(10, 2),
    expected=5.0,
    description='делится нацело',
    level="smoke",
)

@case(
    args=(7, 2),
    expected=3.5,
    description='дробный результат',
    level="smoke",
)

@case(
    args=(5, 0),
    expected="деление на ноль",
    description='делитель ноль',
    level="smoke",
)

@case(
    args=(0, 4),
    expected=0.0,
    description='ноль делим на число',
    level="full",
)

@case(
    args=(0, 0),
    expected="деление на ноль",
    description='ноль на ноль',
    level="full",
)

@case(
    args=(-9, 3),
    expected=-3.0,
    description='отрицательное делимое',
    level="full",
)


@rules(
    forbid_nodes=["If", "IfExp"],
    messages={
        "If": "в этой задаче нужен try/except ZeroDivisionError, а не if",
        "IfExp": "в этой задаче нужен try/except ZeroDivisionError, а не условное выражение",
    },
)

def task_er05_safe_divide(a, b):
    ...
