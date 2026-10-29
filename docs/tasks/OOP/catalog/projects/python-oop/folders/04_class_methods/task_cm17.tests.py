from ego.testing import case, rules

@rules(
    require_classes=['Quest'],
    require_methods={'Quest': ['__init__', 'from_dict', 'from_string']},
    require_decorators={'Quest.from_dict': ['classmethod'], 'Quest.from_string': ['classmethod']},
)
@case(
    args=('dict', {'title': 'Волки', 'reward': 50}),
    expected=['Волки', 50],
    description='старое: квест из словаря',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('dict', {'title': 'Лис'}),
    expected=['Лис', 0],
    description='старое: награды в словаре нет',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('string', 'Волки:50'),
    expected=['Волки', 50],
    description='новое: название и награда',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('string', 'Лис'),
    expected=['Лис', 0],
    description='новое: награды нет',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('string', 'Драконы:0'),
    expected=['Драконы', 0],
    description='новое: награда ноль',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('string', 'Босс:1000'),
    expected=['Босс', 1000],
    description='новое: большая награда',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('dict', {'title': 'Крысы', 'reward': 5, 'done': True}),
    expected=['Крысы', 5],
    description='старое: лишний ключ',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cm17_quest(kind, value):
    ...
