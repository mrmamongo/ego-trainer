from ego.testing import case, rules

@case(
    args=([3, 4, 0, 5],),
    expected=7,
    description='после нуля есть числа',
    level="smoke",
)

@case(
    args=([1, 2, 3],),
    expected=6,
    description='нуля нет',
    level="smoke",
)

@case(
    args=([0, 9],),
    expected=0,
    description='ноль первый',
    level="smoke",
)

@case(
    args=([],),
    expected=0,
    description='пустой список',
    level="full",
)

@case(
    args=([-2, 5, 0, 100],),
    expected=3,
    description='отрицательные учитываются',
    level="full",
)

@case(
    args=([2, 0, 0, 3],),
    expected=2,
    description='несколько нулей',
    level="full",
)

@case(
    args=([0],),
    expected=0,
    description='только ноль',
    level="full",
)


@rules(forbid_names=["sum"])

def task_bk05_sum_until_zero(numbers):
    ...
