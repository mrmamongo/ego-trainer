from ego.testing import case, rules

@rules(
    require_classes=['Score'],
    require_decorators={'Score': ['dataclass']},
    require_functions=['add_points'],
)
@case(
    args=([['Аня', 10], ['Боря', 5]], 'Аня', 3),
    expected={'frozen': True, 'table': [['Аня', 13], ['Боря', 5]]},
    description='бонус одному игроку, запись осталась замороженной',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Аня', 10], ['Боря', 5]], 'Боря', 0),
    expected={'frozen': True, 'table': [['Аня', 10], ['Боря', 5]]},
    description='нулевой бонус',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Вика', 7]], 'Вика', 100),
    expected={'frozen': True, 'table': [['Вика', 107]]},
    description='единственный игрок',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Аня', 1], ['Аня', 2]], 'Аня', 10),
    expected={'frozen': True, 'table': [['Аня', 11], ['Аня', 12]]},
    description='игрок записан дважды',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Аня', 10]], 'Боря', 5),
    expected={'frozen': True, 'table': [['Аня', 10]]},
    description='такого игрока нет',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Аня', 10]], 'Аня', -4),
    expected={'frozen': True, 'table': [['Аня', 6]]},
    description='отрицательный бонус',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([], 'Аня', 5),
    expected={'frozen': True, 'table': []},
    description='пустая таблица',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_dc06_add_points(rows, player, bonus):
    ...
