from ego.testing import case

@case(
    args=([[1, 2], [3, 4]], 4),
    expected=[1, 1],
    description='в конце',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([[1, 2], [3, 4]], 1),
    expected=[0, 0],
    description='в начале',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([[1, 2], [3, 4]], 9),
    expected=[-1, -1],
    description='нет такого',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([], 1),
    expected=[-1, -1],
    description='пустая таблица',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([[1, 2], [2, 1]], 2),
    expected=[0, 1],
    description='первое из нескольких',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([[], [7]], 7),
    expected=[1, 0],
    description='пустая строка перед находкой',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([[1, 2, 3], [4], [5, 6]], 6),
    expected=[2, 1],
    description='строки разной длины',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([[0]], 0),
    expected=[0, 0],
    description='ноль',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

def task_li20_find_in_matrix(matrix, x):
    ...
