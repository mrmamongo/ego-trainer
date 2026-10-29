from ego.testing import case, rules

@rules(
    require_classes=['Player'],
    require_methods={'Player': ['__init__', 'take_damage']},
)
@case(
    args=([['new', 'Аня', 30], ['take_damage', 10], ['get', 'hp']],),
    expected=['ok', 20, 20],
    description='обычный урон',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Боря', 5], ['take_damage', 50]],),
    expected=['ok', 0],
    description='урон больше здоровья',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Вика', 10], ['take_damage', 10]],),
    expected=['ok', 0],
    description='ровно в ноль',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Юра', 40], ['take_damage', 15], ['take_damage', 15], ['take_damage', 15]],),
    expected=['ok', 25, 10, 0],
    description='три удара подряд',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Ира', 7], ['take_damage', 0], ['get', 'hp']],),
    expected=['ok', 7, 7],
    description='нулевой урон',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cl07_damage(actions):
    ...
