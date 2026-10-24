from ego.testing import case

@case(
    args=([1, 2, 3], 'double'),
    expected=[2, 4, 6],
    description='удвоить',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=([1, -2, 3], 'square'),
    expected=[1, 4, 9],
    description='квадрат',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=([1, -2], 'negate'),
    expected=[-1, 2],
    description='сменить знак',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=([5], 'unknown'),
    expected=[5],
    description='неизвестное правило ничего не меняет',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=([], 'double'),
    expected=[],
    description='пустой список',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=([0, 4], 'negate'),
    expected=[0, -4],
    description='ноль при смене знака',
    level="full",
    check_inputs_unchanged=True,
)

def task_fd16_apply(nums, rule):
    ...
