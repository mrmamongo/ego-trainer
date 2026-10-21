from ego.testing import case

@case(
    args=([1, 5, 10, 15], 5, 10),
    expected=2,
    description='обе границы включаются',
    level="smoke",
)

@case(
    args=([1, 2, 3], 10, 20),
    expected=0,
    description='в диапазоне никого нет',
    level="smoke",
)

@case(
    args=([5, 5, 5], 5, 5),
    expected=3,
    description='диапазон из одной точки',
    level="smoke",
)

@case(
    args=([], 0, 10),
    expected=0,
    description='пустой список',
    level="full",
)

@case(
    args=([-3, -1, 0, 2], -2, 1),
    expected=2,
    description='отрицательные границы',
    level="full",
)

@case(
    args=([4, 9], 5, 8),
    expected=0,
    description='числа по обе стороны диапазона',
    level="full",
)

@case(
    args=([1, 2, 3, 4, 5], 1, 5),
    expected=5,
    description='все числа в диапазоне',
    level="full",
)

@case(
    args=([7], 7, 7),
    expected=1,
    description='один элемент на границе',
    level="full",
)
def task_l24_count_in_range(numbers, low, high):
    ...
