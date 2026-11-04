from ego.testing import case, rules

@rules(
    require_classes=['Unit', 'Warrior', 'Mage', 'Archer'],
    require_bases={'Warrior': ['Unit'], 'Mage': ['Unit'], 'Archer': ['Unit']},
    require_methods={'Unit': ['__init__', 'attack', 'take_damage'], 'Warrior': ['attack', 'take_damage'], 'Mage': ['__init__', 'attack'], 'Archer': ['attack']},
)
@case(
    args=([['new', 'Unit', 'Тень', 10], ['attack'], ['take_damage', 4], ['get', 'hp']],),
    expected=['ok', 5, 6, 6],
    description='обычный юнит',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Warrior', 'Грок', 40], ['attack'], ['take_damage', 10], ['get', 'name'], ['is', 'Unit']],),
    expected=['ok', 12, 32, 'Грок', True],
    description='воин и его броня',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Mage', 'Мерлин', 30, 50], ['attack'], ['get', 'mana'], ['get', 'hp']],),
    expected=['ok', 10, 50, 30],
    description='у мага есть мана',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Archer', 'Робин', 25], ['attack'], ['take_damage', 30], ['get', 'hp']],),
    expected=['ok', 8, 0, 0],
    description='лучник и hp не ниже нуля',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Warrior', 'Слабый', 5], ['take_damage', 1], ['take_damage', 2], ['take_damage', 100], ['get', 'hp']],),
    expected=['ok', 5, 5, 0, 0],
    description='броня съедает слабые удары',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Mage', 'Новичок', 20, 9], ['attack'], ['set', 'mana', 100], ['attack'], ['is', 'Mage'], ['is', 'Unit']],),
    expected=['ok', 5, 'ok', 15, True, True],
    description='мана растёт, маг тоже Unit',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Unit', 'Гоблин', 3], ['take_damage', 10], ['is', 'Warrior'], ['is', 'Unit']],),
    expected=['ok', 0, False, True],
    description='Unit не воин',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_in09_units(actions):
    ...
