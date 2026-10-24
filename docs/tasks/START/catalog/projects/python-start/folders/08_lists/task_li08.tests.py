from ego.testing import case

@case(
    args=([1, 2, 3, 4, 5], 2),
    expected=[3, 4, 5, 1, 2],
    description='сдвиг на два',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 2, 3], 1),
    expected=[2, 3, 1],
    description='сдвиг на один',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 2, 3], 0),
    expected=[1, 2, 3],
    description='без сдвига',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([], 5),
    expected=[],
    description='пустой список',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 2, 3], 3),
    expected=[1, 2, 3],
    description='полный круг',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 2, 3], 4),
    expected=[2, 3, 1],
    description='больше длины',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([9], 7),
    expected=[9],
    description='один элемент',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 2, 3, 4], 6),
    expected=[3, 4, 1, 2],
    description='почти два круга',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

def task_li08_rotate_left(nums, k):
    ...
