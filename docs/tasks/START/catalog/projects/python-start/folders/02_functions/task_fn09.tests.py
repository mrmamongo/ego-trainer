from ego.testing import case


@case(
    args=(4,),
    expected='чётное',
    description='чётное число',
    level="smoke",
)

@case(
    args=(7,),
    expected='нечётное',
    description='нечётное число',
    level="smoke",
)

@case(
    args=(0,),
    expected='чётное',
    description='ноль — чётное',
    level="smoke",
)

@case(
    args=(-3,),
    expected='нечётное',
    description='отрицательное нечётное (-3 % 2 == 1)',
    level="full",
)

@case(
    args=(-4,),
    expected='чётное',
    description='отрицательное чётное',
    level="full",
)

@case(
    args=(101,),
    expected='нечётное',
    description='большое нечётное',
    level="full",
)
def task_fn09_parity(n):
    ...
