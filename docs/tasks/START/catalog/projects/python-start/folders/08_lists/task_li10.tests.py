from ego.testing import case, rules

@case(
    args=([1, 3, 5], 4),
    expected=[1, 3, 4, 5],
    description='в середину',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 3], 0),
    expected=[0, 1, 3],
    description='в начало',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 3], 9),
    expected=[1, 3, 9],
    description='в конец',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([], 5),
    expected=[5],
    description='пустой список',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([2, 2], 2),
    expected=[2, 2, 2],
    description='равный элемент',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([-5, 0, 5], -1),
    expected=[-5, -1, 0, 5],
    description='отрицательные',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 2, 3, 4], 3),
    expected=[1, 2, 3, 3, 4],
    description='дубликат в середине',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)


@rules(
    forbid_names=["sorted"],
    forbid_methods=["sort", "insert"],
    messages={"insert": "Метод insert использовать нельзя: позицию ищи сам и склеивай куски"},
)

def task_li10_insert_sorted(nums, x):
    ...
