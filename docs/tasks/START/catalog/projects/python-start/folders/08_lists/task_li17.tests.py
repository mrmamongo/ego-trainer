from ego.testing import case

@case(
    args=([1, 2, 3, 4, 5], 2),
    expected=[[1, 2], [3, 4], [5]],
    description='последний кусок короче',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 2, 3, 4], 2),
    expected=[[1, 2], [3, 4]],
    description='делится нацело',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 2, 3], 5),
    expected=[[1, 2, 3]],
    description='порция больше списка',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([], 3),
    expected=[],
    description='пустой список',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 2, 3], 1),
    expected=[[1], [2], [3]],
    description='по одному',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 2, 3, 4, 5, 6, 7], 3),
    expected=[[1, 2, 3], [4, 5, 6], [7]],
    description='семь по три',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([9], 1),
    expected=[[9]],
    description='один элемент',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

def task_li17_chunk(nums, size):
    ...
