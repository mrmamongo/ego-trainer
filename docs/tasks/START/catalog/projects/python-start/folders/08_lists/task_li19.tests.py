from ego.testing import case

@case(
    args=([[1, 2], [3, 4]],),
    expected=[3, 7],
    description='две строки',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([[5]],),
    expected=[5],
    description='одна строка из одного числа',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([[1, 2, 3], [4, 5, 6]],),
    expected=[6, 15],
    description='по три числа',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([],),
    expected=[],
    description='пустая таблица',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([[5], [], [1, -1]],),
    expected=[5, 0, 0],
    description='пустая строка',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([[-1, -2], [10, -10]],),
    expected=[-3, 0],
    description='отрицательные',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([[0, 0, 0]],),
    expected=[0],
    description='нули',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

def task_li19_row_sums(matrix):
    ...
