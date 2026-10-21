from ego.testing import case


@case(
    args=(1, 2, 3),
    expected=3,
    description='максимум последний',
    level="smoke",
)

@case(
    args=(3, 2, 1),
    expected=3,
    description='максимум первый',
    level="smoke",
)

@case(
    args=(2, 3, 1),
    expected=3,
    description='максимум в середине',
    level="smoke",
)

@case(
    args=(5, 5, 5),
    expected=5,
    description='все равны',
    level="full",
)

@case(
    args=(-1, -5, -3),
    expected=-1,
    description='все отрицательные',
    level="full",
)

@case(
    args=(4, 4, 2),
    expected=4,
    description='два равных максимума в начале',
    level="full",
)

@case(
    args=(2, 4, 4),
    expected=4,
    description='два равных максимума в конце',
    level="full",
)

@case(
    args=(0, -1, -2),
    expected=0,
    description='ноль среди отрицательных',
    level="full",
)
def task_fn15_max3(a, b, c):
    ...
