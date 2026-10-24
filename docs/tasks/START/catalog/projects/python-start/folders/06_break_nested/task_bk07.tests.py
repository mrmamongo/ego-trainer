from ego.testing import case

@case(
    args=(1, 10, 3),
    expected=3,
    description='первое кратное трём',
    level="smoke",
)

@case(
    args=(4, 10, 5),
    expected=5,
    description='кратное в середине',
    level="smoke",
)

@case(
    args=(8, 10, 7),
    expected=-1,
    description='нет кратных',
    level="smoke",
)

@case(
    args=(7, 7, 7),
    expected=7,
    description='отрезок из одного числа',
    level="full",
)

@case(
    args=(1, 1, 2),
    expected=-1,
    description='одно число и не делится',
    level="full",
)

@case(
    args=(0, 5, 3),
    expected=0,
    description='ноль делится',
    level="full",
)

@case(
    args=(-5, 5, 4),
    expected=-4,
    description='отрицательная граница',
    level="full",
)

@case(
    args=(5, 3, 2),
    expected=-1,
    description='пустой отрезок',
    level="full",
)
def task_bk07_first_multiple(a, b, k):
    ...
