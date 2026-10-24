from ego.testing import case, rules

@case(
    args=([1, 4], [2, 3, 5]),
    expected=[1, 2, 3, 4, 5],
    description='перемешаны',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([], [1, 2]),
    expected=[1, 2],
    description='первый пуст',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([3, 4], []),
    expected=[3, 4],
    description='второй пуст',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([], []),
    expected=[],
    description='оба пусты',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 1], [1]),
    expected=[1, 1, 1],
    description='равные',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 2], [5, 6]),
    expected=[1, 2, 5, 6],
    description='всё из a раньше',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([5, 6], [1, 2]),
    expected=[1, 2, 5, 6],
    description='всё из b раньше',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([-3, 0, 4], [-1, 0, 9, 10]),
    expected=[-3, -1, 0, 0, 4, 9, 10],
    description='с отрицательными',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)


@rules(forbid_names=["sorted"], forbid_methods=["sort"])

def task_li21_merge_sorted(a, b):
    ...
