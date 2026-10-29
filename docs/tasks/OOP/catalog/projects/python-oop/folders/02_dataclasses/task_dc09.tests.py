from ego.testing import case, rules

@rules(
    require_classes=['Player'],
    require_decorators={'Player': ['dataclass']},
    require_methods={'Player': ['take_damage', 'heal', 'is_alive']},
)
@case(
    args=([['new', 'Аня'], ['get', 'hp'], ['take_damage', 30], ['is_alive']],),
    expected=['ok', 100, 70, True],
    description='здоровье по умолчанию и урон',
    level='smoke',
    comparison='value',
)
@case(
    args=([['new', 'Боря', 50], ['take_damage', 80], ['is_alive'], ['get', 'hp']],),
    expected=['ok', 0, False, 0],
    description='здоровье не уходит ниже нуля',
    level='smoke',
    comparison='value',
)
@case(
    args=([['new', 'Вика', 40], ['heal', 70], ['get', 'hp']],),
    expected=['ok', 100, 100],
    description='лечение не больше 100',
    level='smoke',
    comparison='value',
)
@case(
    args=([['new', 'Аня'], ['take_damage', -5], ['get', 'hp']],),
    expected=['ok', ['error', 'ValueError', 'урон не может быть отрицательным'], 100],
    description='отрицательный урон — ошибка, здоровье не меняется',
    level='full',
    comparison='value',
)
@case(
    args=([['new', 'Аня'], ['take_damage', 60], ['heal', 25], ['get', 'hp']],),
    expected=['ok', 40, 65, 65],
    description='урон, потом лечение',
    level='full',
    comparison='value',
)
@case(
    args=([['new', 'Аня', 30], ['take_damage', 30], ['is_alive']],),
    expected=['ok', 0, False],
    description='ровно ноль здоровья — не жив',
    level='full',
    comparison='value',
)
@case(
    args=([['new', 'Ира', 1], ['get', 'name'], ['is_alive']],),
    expected=['ok', 'Ира', True],
    description='один пункт здоровья — жив',
    level='full',
    comparison='value',
)
def task_dc09_player(actions):
    ...
