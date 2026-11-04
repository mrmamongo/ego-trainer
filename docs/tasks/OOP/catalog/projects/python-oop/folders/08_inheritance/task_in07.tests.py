from ego.testing import case, rules

@rules(
    require_classes=['Unit', 'Archer'],
    require_bases={'Archer': ['Unit']},
    require_methods={'Unit': ['__init__', 'attack'], 'Archer': ['attack']},
)
@case(
    args=([['new', 'Archer', 'Робин', 1], ['attack']],),
    expected=['ok', 10],
    description='первый уровень',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Archer', 'Леголас', 3], ['attack']],),
    expected=['ok', 14],
    description='третий уровень',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Unit', 'Ополченец', 3], ['attack']],),
    expected=['ok', 7],
    description='родитель бьёт как раньше',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Archer', 'Новичок', 0], ['attack'], ['get', 'level']],),
    expected=['ok', 8, 0],
    description='нулевой уровень',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Archer', 'Ветеран', 10], ['attack'], ['set', 'level', 11], ['attack']],),
    expected=['ok', 28, 'ok', 30],
    description='уровень вырос',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Archer', 'Эльф', 2], ['is', 'Unit'], ['attack']],),
    expected=['ok', True, 12],
    description='лучник тоже Unit',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_in07_archer(actions):
    ...
