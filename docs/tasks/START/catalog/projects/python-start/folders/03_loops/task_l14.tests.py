from ego.testing import case

@case(
    args=([1, 2, 3], 3),
    expected=True,
    description='искомое в конце',
    level="smoke",
)

@case(
    args=([4, 5, 6], 4),
    expected=True,
    description='искомое в начале',
    level="smoke",
)

@case(
    args=([4, 5, 6], 9),
    expected=False,
    description='искомого нет',
    level="smoke",
)

@case(
    args=([], 1),
    expected=False,
    description='пустой список',
    level="full",
)

@case(
    args=([7], 7),
    expected=True,
    description='единственный элемент',
    level="full",
)

@case(
    args=([1, 2, 1], 1),
    expected=True,
    description='встречается дважды',
    level="full",
)

@case(
    args=([2, 4, 6, 8], 8),
    expected=True,
    description='искомое последнее',
    level="full",
)
def task_l14_contains(numbers, target):
    ...
