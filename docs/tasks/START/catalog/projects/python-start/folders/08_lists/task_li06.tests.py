from ego.testing import case

@case(
    args=([3, 1, 2],),
    expected=[1, 2, 3],
    description='простой список',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([5, 4, 3, 2, 1],),
    expected=[1, 2, 3, 4, 5],
    description='обратный порядок',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([2, 2, 1],),
    expected=[1, 2, 2],
    description='повторы',
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
    args=([7],),
    expected=[7],
    description='один элемент',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 2, 3],),
    expected=[1, 2, 3],
    description='уже отсортирован',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([-3, 5, 0, -10],),
    expected=[-10, -3, 0, 5],
    description='отрицательные',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

def task_li06_sorted_copy(nums):
    ...
