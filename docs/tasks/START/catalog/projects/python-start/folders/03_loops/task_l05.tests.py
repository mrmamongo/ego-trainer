from ego.testing import case, rules

@case(
    args=([1, 2, 3],),
    expected=6,
    description='простой список',
    level="smoke",
)

@case(
    args=([5, 5],),
    expected=10,
    description='два одинаковых числа',
    level="smoke",
)

@case(
    args=([10, 20, 30],),
    expected=60,
    description='три числа',
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
    expected=-3,
    description='отрицательные',
    level="full",
)

@case(
    args=([10, 20, 30, 40],),
    expected=100,
    description='четыре числа',
    level="full",
)


@rules(forbid_names=["sum"])

def task_l05_sum_all(numbers):
    ...
