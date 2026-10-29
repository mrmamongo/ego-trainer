from ego.testing import case, rules

@rules(
    require_functions=['add_bonus'],
)
@case(
    args=(3, 2),
    expected=11,
    description='6 плюс бонус 5',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(10, 1),
    expected=15,
    description='10 плюс бонус 5',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(0, 5),
    expected=5,
    description='удар нулевой, бонус остаётся',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(4, 0),
    expected=5,
    description='нулевой уровень',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(7, 7),
    expected=54,
    description='49 плюс бонус',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(100, 3),
    expected=305,
    description='большое число',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cm06_bonus(power, level):
    ...
