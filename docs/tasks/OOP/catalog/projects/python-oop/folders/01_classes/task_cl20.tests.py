from ego.testing import case, rules

@rules(
    require_classes=['Player'],
    require_methods={'Player': ['__init__', 'take_damage']},
)
@case(
    args=([['new', 'Аня', 30], ['take_damage', 10]],),
    expected=['ok', 20],
    description='старое поведение без брони',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Боря', 5], ['take_damage', 50]],),
    expected=['ok', 0],
    description='старая граница: не ниже нуля',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Вика', 30, 4], ['take_damage', 10], ['get', 'armor']],),
    expected=['ok', 24, 4],
    description='броня уменьшает удар',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Юра', 30, 5], ['take_damage', 3], ['get', 'hp']],),
    expected=['ok', 30, 30],
    description='броня съела весь удар',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Ира', 10, 2], ['take_damage', 50]],),
    expected=['ok', 0],
    description='броня есть, hp всё равно в ноль',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Лев', 10], ['get', 'armor']],),
    expected=['ok', 0],
    description='броня по умолчанию',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Мия', 10, 3], ['take_damage', 4], ['take_damage', 4]],),
    expected=['ok', 9, 8],
    description='два удара подряд',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cl20_armor(actions):
    ...
