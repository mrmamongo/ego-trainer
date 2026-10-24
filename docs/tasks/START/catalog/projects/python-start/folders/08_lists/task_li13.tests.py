from ego.testing import case

@case(
    args=([1, 2, 3, 4],),
    expected=[4, 16],
    description='чётные и нечётные',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([2, 6],),
    expected=[4, 36],
    description='все чётные',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 3],),
    expected=[],
    description='ни одного чётного',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([],),
    expected=[],
    description='пустой список',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([-2, 3, 0],),
    expected=[4, 0],
    description='отрицательное и ноль',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([10, 7, 8, 9],),
    expected=[100, 64],
    description='порядок сохраняется',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

def task_li13_even_squares(nums):
    ...
