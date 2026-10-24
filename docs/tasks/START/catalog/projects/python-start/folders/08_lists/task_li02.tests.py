from ego.testing import case

@case(
    args=([1, 2, 3, 4],),
    expected=[4, 2, 3, 1],
    description='четыре элемента',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([7, 8],),
    expected=[8, 7],
    description='два элемента',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([5],),
    expected=[5],
    description='один элемент',
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
    args=([1, 2, 1],),
    expected=[1, 2, 1],
    description='концы равны',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([4, 5, 6, 7, 8],),
    expected=[8, 5, 6, 7, 4],
    description='нечётная длина',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([-1, 0, 3],),
    expected=[3, 0, -1],
    description='отрицательные',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

def task_li02_swap_ends(nums):
    ...
