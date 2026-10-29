from ego.testing import case, rules

@rules(
    require_classes=['Card'],
    require_methods={'Card': ['__init__', '__eq__']},
)
@case(
    args=([['Q', 'червы'], ['K', 'пики'], ['Q', 'червы']],),
    expected=[['Q', 'червы', 2], ['K', 'пики', 1]],
    description='повтор дамы',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['7', 'бубны']],),
    expected=[['7', 'бубны', 1]],
    description='одна карта',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Q', 'червы'], ['Q', 'пики']],),
    expected=[['Q', 'червы', 1], ['Q', 'пики', 1]],
    description='один ранг, разные масти',
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
    args=([['A', 'трефы'], ['A', 'трефы'], ['A', 'трефы'], ['A', 'трефы']],),
    expected=[['A', 'трефы', 4]],
    description='четыре одинаковые',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['10', 'пики'], ['J', 'пики'], ['10', 'червы'], ['10', 'пики'], ['J', 'пики']],),
    expected=[['10', 'пики', 2], ['J', 'пики', 2], ['10', 'червы', 1]],
    description='порядок первых вхождений',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mg18_tally(rows):
    ...
