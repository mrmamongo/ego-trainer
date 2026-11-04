from ego.testing import case, rules

@rules(
    require_classes=['Leaderboard'],
    require_methods={'Leaderboard': ['__init__', '__iter__']},
)
@case(
    args=([['Аня', 50], ['Боря', 80], ['Вика', 65]],),
    expected=[['1. Боря: 80', '2. Вика: 65', '3. Аня: 50'], ['1. Боря: 80', '2. Вика: 65', '3. Аня: 50']],
    description='все места, по убыванию',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Аня', 50], ['Боря', 80], ['Вика', 65]], 2),
    expected=[['1. Боря: 80', '2. Вика: 65'], ['1. Боря: 80', '2. Вика: 65']],
    description='только два первых места',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Аня', 50]], 1),
    expected=[['1. Аня: 50'], ['1. Аня: 50']],
    description='один игрок',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected=[[], []],
    description='пустая таблица',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([], 3),
    expected=[[], []],
    description='пустая таблица с top',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['А', 5], ['Б', 5], ['В', 7]],),
    expected=[['1. В: 7', '2. А: 5', '3. Б: 5'], ['1. В: 7', '2. А: 5', '3. Б: 5']],
    description='равные очки в прежнем порядке',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['А', 1], ['Б', 2]], 10),
    expected=[['1. Б: 2', '2. А: 1'], ['1. Б: 2', '2. А: 1']],
    description='top больше длины',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['А', 1], ['Б', 2]], 0),
    expected=[[], []],
    description='top равен нулю',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pt17_board(rows, top=None):
    ...
