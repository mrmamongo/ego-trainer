from ego.testing import case

@case(
    args=([5, 9, 1, 7, 3],),
    expected=[9, 7, 5],
    description='обычный список',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([4, 2],),
    expected=[4, 2],
    description='меньше трёх',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 2, 3],),
    expected=[3, 2, 1],
    description='ровно три',
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
    args=([5, 5, 3, 1],),
    expected=[5, 5, 3],
    description='повторы',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([-1, -5, -3, -2],),
    expected=[-1, -2, -3],
    description='отрицательные',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([8],),
    expected=[8],
    description='один элемент',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

def task_li11_top3(nums):
    ...
