from ego.testing import case, rules

@case(
    args=([1, 2, 1, 3], 1),
    expected=[2, 3],
    description='несколько вхождений',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([4, 5], 9),
    expected=[4, 5],
    description='нет такого',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([2, 2], 2),
    expected=[],
    description='убрали всё',
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
    args=([1, 2, 3], 3),
    expected=[1, 2],
    description='последний элемент',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([5, 5, 6, 5, 7], 5),
    expected=[6, 7],
    description='вхождения не подряд',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([0, -1, 0], 0),
    expected=[-1],
    description='ноль',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)


@rules(forbid_methods=["remove"])

def task_li07_remove_all(nums, x):
    ...
