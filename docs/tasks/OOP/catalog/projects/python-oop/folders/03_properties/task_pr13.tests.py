from ego.testing import case, rules

@rules(
    require_classes=['Player'],
    require_decorators={'Player.hp': ['property'], 'Player.is_alive': ['property']},
    require_methods={'Player': ['__init__', 'damage', 'heal']},
    forbid_attributes_outside_class=['_hp'],
)
@case(
    args=([['new', 'Аня', 30], ['get', 'hp'], ['damage', 10], ['get', 'hp']],),
    expected=['ok', 30, None, 20],
    description='урон уменьшает hp',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Боря', 30], ['damage', 20], ['heal', 100], ['get', 'hp']],),
    expected=['ok', None, None, 30],
    description='лечение не выше максимума',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Вика', 10], ['damage', 100], ['get', 'hp'], ['get', 'is_alive']],),
    expected=['ok', None, 0, False],
    description='hp не ниже нуля, игрок погиб',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Юра', 50], ['set', 'hp', -7], ['get', 'hp'], ['set', 'hp', 99], ['get', 'hp']],),
    expected=['ok', 'ok', 0, 'ok', 50],
    description='присваивание тоже подрезается',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Ира', 5], ['damage', 5], ['get', 'is_alive'], ['heal', 1], ['get', 'is_alive']],),
    expected=['ok', None, False, None, True],
    description='ровно ноль и воскрешение',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Лев', 40], ['set', 'is_alive', True], ['get', 'name'], ['get', 'max_hp']],),
    expected=['ok', ['error', 'AttributeError', ''], 'Лев', 40],
    description='is_alive только для чтения',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Мия', 20], ['damage', 0], ['heal', 0], ['get', 'hp']],),
    expected=['ok', None, None, 20],
    description='нулевые изменения',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pr13_player(actions):
    ...
