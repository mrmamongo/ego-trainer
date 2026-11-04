from ego.testing import case, rules

@rules(
    require_classes=['QuestLog'],
    require_methods={'QuestLog': ['__init__', 'add', 'finish', '__iter__']},
)
@case(
    args=([['add', 'a'], ['add', 'b'], ['finish', 'a']],),
    expected=['ok', 'ok', 'ok', ['b'], ['b']],
    description='один выполнен',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['add', 'a']],),
    expected=['ok', ['a'], ['a']],
    description='один квест',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['finish', 'a']],),
    expected=['нет такого квеста', [], []],
    description='нет такого квеста',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected=[[], []],
    description='пустой журнал',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['add', 'a'], ['add', 'a']],),
    expected=['ok', 'квест уже есть', ['a'], ['a']],
    description='повторное добавление',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['add', 'a'], ['finish', 'a'], ['finish', 'a']],),
    expected=['ok', 'ok', 'ok', [], []],
    description='повторное finish не ошибка',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['add', 'x'], ['add', 'y'], ['add', 'z'], ['finish', 'y'], ['add', 'w']],),
    expected=['ok', 'ok', 'ok', 'ok', 'ok', ['x', 'z', 'w'], ['x', 'z', 'w']],
    description='порядок остаётся',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pt12_quests(actions):
    ...
