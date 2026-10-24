from ego.testing import case

@case(
    args=([1, 2, 3],),
    expected=[1, 4, 9],
    description='три числа',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([-2, 0],),
    expected=[4, 0],
    description='отрицательное и ноль',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([5],),
    expected=[25],
    description='одно число',
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
    args=([10, -10, 3],),
    expected=[100, 100, 9],
    description='противоположные',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 1, 1],),
    expected=[1, 1, 1],
    description='повторы',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

def task_li14_squares(nums):
    ...
