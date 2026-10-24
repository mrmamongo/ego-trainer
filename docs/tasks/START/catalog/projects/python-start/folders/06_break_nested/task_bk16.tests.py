from ego.testing import case

@case(
    args=([1, 2, 3], [3, 4]),
    expected=True,
    description='общий в конце первого и начале второго',
    level="smoke",
)

@case(
    args=([1, 2], [3, 4]),
    expected=False,
    description='общих нет',
    level="smoke",
)

@case(
    args=([5], [5]),
    expected=True,
    description='по одному одинаковому',
    level="smoke",
)

@case(
    args=([], [1]),
    expected=False,
    description='первый список пуст',
    level="full",
)

@case(
    args=([1], []),
    expected=False,
    description='второй список пуст',
    level="full",
)

@case(
    args=([1, 2, 3], [0, 9, 2]),
    expected=True,
    description='общий в середине',
    level="full",
)

@case(
    args=([7, 7], [8, 8]),
    expected=False,
    description='повторы без общих',
    level="full",
)

@case(
    args=([1, 2], [3, 2]),
    expected=True,
    description='общий найден не на первой паре',
    level="full",
)
def task_bk16_has_common(a, b):
    ...
