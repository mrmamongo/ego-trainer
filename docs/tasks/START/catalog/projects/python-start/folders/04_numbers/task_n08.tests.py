from ego.testing import case

@case(
    args=(3, 4),
    expected=5.0,
    description='египетский треугольник',
    level="smoke",
)

@case(
    args=(1, 1),
    expected=1.4,
    description='корень из двух',
    level="smoke",
)

@case(
    args=(6, 8),
    expected=10.0,
    description='удвоенный треугольник 3-4-5',
    level="smoke",
)

@case(
    args=(5, 12),
    expected=13.0,
    description='треугольник 5-12-13',
    level="full",
)

@case(
    args=(2, 3),
    expected=3.6,
    description='нецелый корень',
    level="full",
)

@case(
    args=(1, 2),
    expected=2.2,
    description='маленькие катеты',
    level="full",
)

@case(
    args=(10, 10),
    expected=14.1,
    description='равные катеты',
    level="full",
)
def task_n08_hypotenuse(a, b):
    ...
