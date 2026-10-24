from ego.testing import case, rules

@case(
    args=([5, -1, 4, 2],),
    expected=11,
    description='после минуса есть числа',
    level="smoke",
)

@case(
    args=([-3, 2, 5],),
    expected=7,
    description='минус в начале',
    level="smoke",
)

@case(
    args=([1, 2, 3],),
    expected=6,
    description='минусов нет',
    level="smoke",
)

@case(
    args=([],),
    expected=0,
    description='пустой список',
    level="full",
)

@case(
    args=([-1, -2],),
    expected=0,
    description='только отрицательные',
    level="full",
)

@case(
    args=([4, -4, 4, -4, 4],),
    expected=12,
    description='минусы чередуются с плюсами',
    level="full",
)

@case(
    args=([0, -5, 0, 3],),
    expected=3,
    description='нули не мешают',
    level="full",
)


@rules(forbid_names=["sum"])

def task_bk04_sum_skip_negative(numbers):
    ...
