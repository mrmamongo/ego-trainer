from ego.testing import case

@case(
    args=([1, 2, 0, 5],),
    expected=3,
    description='старый случай: стоп на нуле',
    level="smoke",
)

@case(
    args=([1, -2, 3],),
    expected=4,
    description='отрицательное пропускается',
    level="smoke",
)

@case(
    args=([4, -1, 0, 9],),
    expected=4,
    description='пропуск и стоп вместе',
    level="smoke",
)

@case(
    args=([-1, -2],),
    expected=0,
    description='только отрицательные',
    level="full",
)

@case(
    args=([5, 0, -1],),
    expected=5,
    description='после нуля ничего не считается',
    level="full",
)

@case(
    args=([0, 3],),
    expected=0,
    description='ноль первым',
    level="full",
)

@case(
    args=([],),
    expected=0,
    description='пустой список',
    level="full",
)

@case(
    args=([-5, 0, 7],),
    expected=0,
    description='отрицательное, ноль, потом число',
    level="full",
)

@case(
    args=([2, 3],),
    expected=5,
    description='нуля нет, минусов нет',
    level="full",
)

def task_fd10_sum_until_zero(nums):
    ...
