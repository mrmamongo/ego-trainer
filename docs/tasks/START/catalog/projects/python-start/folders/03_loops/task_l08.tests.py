from ego.testing import case

@case(
    args=([1, -2, 3],),
    expected=2,
    description='смесь знаков',
    level="smoke",
)

@case(
    args=([5, 6, 7],),
    expected=3,
    description='все положительные',
    level="smoke",
)

@case(
    args=([-1, -2],),
    expected=0,
    description='ни одного положительного',
    level="smoke",
)

@case(
    args=([],),
    expected=0,
    description='пустой список',
    level="full",
)

@case(
    args=([0, 0],),
    expected=0,
    description='ноль не положительный',
    level="full",
)

@case(
    args=([0, 1],),
    expected=1,
    description='ноль и единица',
    level="full",
)

@case(
    args=([-5, 10, -20, 30, 0],),
    expected=2,
    description='разные числа',
    level="full",
)
def task_l08_count_positive(numbers):
    ...
