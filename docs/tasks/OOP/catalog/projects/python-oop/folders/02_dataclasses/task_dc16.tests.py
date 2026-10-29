from ego.testing import case, rules

@rules(
    require_classes=['Score'],
    require_decorators={'Score': ['dataclass']},
    require_functions=['apply_bonus'],
)
@case(
    args=([['Аня', 60], ['Боря', 20]], 10),
    expected={'frozen': True, 'before': [['Аня', 60], ['Боря', 20]], 'after': [['Аня', 70], ['Боря', 20]]},
    description='бонус получает только тот, у кого от 50 очков',
    level='smoke',
    comparison='value',
)
@case(
    args=([['Вика', 50]], 5),
    expected={'frozen': True, 'before': [['Вика', 50]], 'after': [['Вика', 55]]},
    description='ровно 50 очков — бонус есть',
    level='smoke',
    comparison='value',
)
@case(
    args=([], 10),
    expected={'frozen': True, 'before': [], 'after': []},
    description='пустая таблица',
    level='smoke',
    comparison='value',
)
@case(
    args=([['Аня', 10], ['Боря', 49]], 100),
    expected={'frozen': True, 'before': [['Аня', 10], ['Боря', 49]], 'after': [['Аня', 10], ['Боря', 49]]},
    description='никто не дотянул до 50',
    level='full',
    comparison='value',
)
@case(
    args=([['Аня', 80], ['Боря', 90], ['Вика', 70]], -20),
    expected={'frozen': True, 'before': [['Аня', 80], ['Боря', 90], ['Вика', 70]], 'after': [['Аня', 60], ['Боря', 70], ['Вика', 50]]},
    description='отрицательный бонус, порядок сохраняется',
    level='full',
    comparison='value',
)
@case(
    args=([['Аня', 50], ['Аня', 20]], 1),
    expected={'frozen': True, 'before': [['Аня', 50], ['Аня', 20]], 'after': [['Аня', 51], ['Аня', 20]]},
    description='один игрок дважды',
    level='full',
    comparison='value',
)
def task_dc16_bonus(rows, bonus):
    ...
