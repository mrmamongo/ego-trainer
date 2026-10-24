from ego.testing import case

@case(
    args=([3, -1, 0, 5],),
    expected=[3, 5],
    description='смесь',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 2, 3],),
    expected=[1, 2, 3],
    description='все положительные',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([-2, -3],),
    expected=[],
    description='ни одного положительного',
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
    args=([0, 0],),
    expected=[],
    description='только нули',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([5, -5, 5, -5, 7],),
    expected=[5, 5, 7],
    description='порядок и повторы',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

def task_li15_positives(nums):
    ...
