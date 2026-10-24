from ego.testing import case

@case(
    args=([[1, 2, 3], [4, 5, 6]],),
    expected=[[1, 4], [2, 5], [3, 6]],
    description='две строки, три столбца',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([[1, 2]],),
    expected=[[1], [2]],
    description='одна строка',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([[7]],),
    expected=[[7]],
    description='один элемент',
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
    args=([[1], [2], [3]],),
    expected=[[1, 2, 3]],
    description='один столбец',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([[1, 2], [3, 4]],),
    expected=[[1, 3], [2, 4]],
    description='квадрат',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([[1, 2], [3, 4], [5, 6]],),
    expected=[[1, 3, 5], [2, 4, 6]],
    description='три строки',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

def task_li18_transpose(matrix):
    ...
