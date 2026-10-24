from ego.testing import case

@case(
    args=([1, 2], [3, 4]),
    expected=2,
    description='две пары из четырёх',
    level="smoke",
)

@case(
    args=([2, 4], [6]),
    expected=2,
    description='все пары чётные',
    level="smoke",
)

@case(
    args=([1], [2]),
    expected=0,
    description='ни одной пары',
    level="smoke",
)

@case(
    args=([], [1, 2]),
    expected=0,
    description='первый список пуст',
    level="full",
)

@case(
    args=([1, 2], []),
    expected=0,
    description='второй список пуст',
    level="full",
)

@case(
    args=([1, 3, 5], [1, 3]),
    expected=6,
    description='нечётные с нечётными',
    level="full",
)

@case(
    args=([1, 2, 3], [1, 2, 3]),
    expected=5,
    description='три на три',
    level="full",
)
def task_bk12_count_even_pairs(a, b):
    ...
