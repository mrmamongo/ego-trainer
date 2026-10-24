from ego.testing import case

@case(
    args=([5, 1, 9], [7, 2], 4),
    expected=(2, 1),
    description='два вызова подряд',
    level="smoke",
)

@case(
    args=([1, 2], [3, 4], 0),
    expected=(2, 2),
    description='все больше нуля',
    level="smoke",
)

@case(
    args=([10], [10], 5),
    expected=(1, 1),
    description='по одному в каждом',
    level="smoke",
)

@case(
    args=([], [], 1),
    expected=(0, 0),
    description='оба списка пустые',
    level="full",
)

@case(
    args=([9, 9], [], 5),
    expected=(2, 0),
    description='второй список пустой',
    level="full",
)

@case(
    args=([], [9, 9], 5),
    expected=(0, 2),
    description='первый список пустой',
    level="full",
)

def task_fd06_report(first, second, limit):
    ...
