from ego.testing import case, rules

@case(
    args=([1, -2, 3],),
    expected=4,
    description='плюсы и минус',
    level="smoke",
)

@case(
    args=([-1, 5, 7],),
    expected=12,
    description='минус в начале',
    level="smoke",
)

@case(
    args=([2, 2, 2],),
    expected=6,
    description='все положительные',
    level="smoke",
)

@case(
    args=([],),
    expected=0,
    description='пустой список',
    level="full",
)

@case(
    args=([-1, 0, -5],),
    expected=0,
    description='нет положительных',
    level="full",
)

@case(
    args=([0, 4, 0, -4, 6],),
    expected=10,
    description='нули и минусы вперемешку',
    level="full",
)


@rules(forbid_names=["sum"])

def task_bk06_sum_positive(numbers):
    ...
