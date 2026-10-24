from ego.testing import case

@case(
    args=({'яблоки': 5}, {'яблоки': 3, 'груши': 2}),
    expected={'яблоки': 8, 'груши': 2},
    description='общий и разный товар',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({}, {'чай': 1}),
    expected={'чай': 1},
    description='первый пуст',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({'чай': 1}, {}),
    expected={'чай': 1},
    description='второй пуст',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({}, {}),
    expected={},
    description='оба пусты',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({'а': 1, 'б': 2}, {'б': 3, 'в': 4}),
    expected={'а': 1, 'б': 5, 'в': 4},
    description='пересечение посередине',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({'а': 0}, {'а': 0}),
    expected={'а': 0},
    description='нули складываются',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
def task_di17_merge_inventories(a, b):
    ...
