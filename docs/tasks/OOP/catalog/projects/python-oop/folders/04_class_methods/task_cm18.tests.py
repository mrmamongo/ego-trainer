from ego.testing import case, rules

@rules(
    require_functions=['announce'],
)
@case(
    args=([5],),
    expected=[[15], [15], 1],
    description='один вызов',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([1, 2, 3],),
    expected=[[11, 12, 13], [11, 12, 13], 3],
    description='три вызова',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected=[[], [], 0],
    description='вызовов не было',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([0, 0],),
    expected=[[10, 10], [10, 10], 2],
    description='нулевые добавки считаются вызовами',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([10, 10, 10, 10, 10],),
    expected=[[20, 20, 20, 20, 20], [20, 20, 20, 20, 20], 5],
    description='пять вызовов',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cm18_calls(amounts):
    ...
