from ego.testing import case

@case(
    args=([1, 2, 3], [4, 5, 6], 7),
    expected=3,
    description='три пары',
    level="smoke",
)

@case(
    args=([1, 1], [2, 2], 3),
    expected=4,
    description='повторяющиеся значения',
    level="smoke",
)

@case(
    args=([1, 2], [3, 4], 100),
    expected=0,
    description='нет подходящих',
    level="smoke",
)

@case(
    args=([], [1], 1),
    expected=0,
    description='первый список пуст',
    level="full",
)

@case(
    args=([1], [], 1),
    expected=0,
    description='второй список пуст',
    level="full",
)

@case(
    args=([5], [5], 10),
    expected=1,
    description='одна пара',
    level="full",
)

@case(
    args=([0, 1, 2], [2, 1, 0], 2),
    expected=3,
    description='нули и обратный порядок',
    level="full",
)

@case(
    args=([3, 3, 3], [4], 7),
    expected=3,
    description='одинаковые первые',
    level="full",
)
def task_bk15_count_pairs_with_sum(a, b, target):
    ...
