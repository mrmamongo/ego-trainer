from ego.testing import case


@case(
    args=(3, 8),
    expected=8,
    description='второе больше',
    level="smoke",
)

@case(
    args=(9, 2),
    expected=9,
    description='первое больше',
    level="smoke",
)

@case(
    args=(5, 5),
    expected=5,
    description='числа равны',
    level="smoke",
)

@case(
    args=(-1, -5),
    expected=-1,
    description='отрицательные числа',
    level="full",
)

@case(
    args=(0, 0),
    expected=0,
    description='два нуля',
    level="full",
)

@case(
    args=(-3, 4),
    expected=4,
    description='числа разных знаков',
    level="full",
)
def task_fn10_bigger(a, b):
    ...
