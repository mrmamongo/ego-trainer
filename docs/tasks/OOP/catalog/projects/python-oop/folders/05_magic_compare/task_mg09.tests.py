from ego.testing import case, rules

@rules(
    require_classes=['Card'],
    require_methods={'Card': ['__init__', '__eq__']},
)
@case(
    args=([[['Q', 'червы'], ['Q', 'червы']]],),
    expected=[[True, False, False]],
    description='одинаковые карты',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[['Q', 'червы'], ['Q', 'пики']]],),
    expected=[[False, True, False]],
    description='разные масти',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[['10', 'пики'], ['J', 'пики']]],),
    expected=[[False, True, False]],
    description='разные ранги',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected=[],
    description='пусто',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[['Q', 'червы'], ['Q', 'червы']], [['Q', 'червы'], ['Q', 'пики']], [['10', 'пики'], ['J', 'пики']]],),
    expected=[[True, False, False], [False, True, False], [False, True, False]],
    description='несколько пар',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[['A', 'трефы'], ['K', 'бубны']]],),
    expected=[[False, True, False]],
    description='разное всё',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mg09_compare(pairs):
    ...
