from ego.testing import case, rules

@case(
    args=([1, 2, 3],),
    expected=6,
    description='простой список',
    level="smoke",
)

@case(
    args=([4, 5],),
    expected=9,
    description='два числа',
    level="smoke",
)

@case(
    args=([10, 20, 30],),
    expected=60,
    description='три числа',
    level="smoke",
)

@case(
    args=([7],),
    expected=7,
    description='один элемент',
    level="full",
)

@case(
    args=([],),
    expected=0,
    description='пустой список',
    level="full",
)

@case(
    args=([-3, 3, -3],),
    expected=-3,
    description='числа разных знаков',
    level="full",
)


@rules(forbid_names=["sum"])

def task_l06_total(numbers):
    ...
