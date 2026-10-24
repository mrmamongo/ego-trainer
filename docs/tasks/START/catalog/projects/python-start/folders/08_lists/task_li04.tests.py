from ego.testing import case

@case(
    args=([1, 2, 3, 4],),
    expected=[2, 3],
    description='четыре элемента',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 2, 3],),
    expected=[2],
    description='три элемента',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([10, 20, 30, 40, 50],),
    expected=[20, 30, 40],
    description='пять элементов',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 2],),
    expected=[],
    description='два элемента',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([5],),
    expected=[],
    description='один элемент',
    level="full",
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
    args=([7, 7, 7],),
    expected=[7],
    description='одинаковые',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

def task_li04_middle(nums):
    ...
