from ego.testing import case, rules

@rules(
    require_classes=['Unit', 'Warrior'],
    require_bases={'Warrior': ['Unit']},
    require_methods={'Unit': ['__init__', 'attack'], 'Warrior': ['attack']},
)
@case(
    args=([['new', 'Unit', 'Ополченец', 3], ['attack']],),
    expected=['ok', 7],
    description='обычный юнит как раньше',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Warrior', 'Грок', 4], ['attack']],),
    expected=['ok', 12],
    description='четвёртый уровень, как раньше',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Warrior', 'Новобранец', 1], ['attack']],),
    expected=['ok', 9],
    description='первый уровень',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Warrior', 'Ярый', 2, 3], ['attack'], ['get', 'rage']],),
    expected=['ok', 13, 3],
    description='ярость прибавляется',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Warrior', 'Спокойный', 5], ['get', 'rage'], ['attack']],),
    expected=['ok', 0, 13],
    description='ярость по умолчанию 0',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Warrior', 'Рост', 4], ['set', 'level', 10], ['attack'], ['is', 'Unit']],),
    expected=['ok', 'ok', 18, True],
    description='удар растёт с уровнем',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Warrior', 'Нулевой', 0, 0], ['attack']],),
    expected=['ok', 8],
    description='нулевой уровень',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_in18_rage(actions):
    ...
