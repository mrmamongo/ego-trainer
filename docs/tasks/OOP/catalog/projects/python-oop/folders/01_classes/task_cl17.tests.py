from ego.testing import case, rules

@rules(
    require_classes=['Quest'],
    require_methods={'Quest': ['__init__', 'start', 'finish', 'is_done']},
)
@case(
    args=([['new', 'Охота'], ['get', 'status'], ['start'], ['get', 'status']],),
    expected=['ok', 'new', None, 'active'],
    description='начало квеста',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Охота'], ['finish']],),
    expected=['ok', ['error', 'ValueError', 'нельзя завершить квест из статуса new']],
    description='завершить неначатый',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Охота'], ['start'], ['finish'], ['is_done']],),
    expected=['ok', None, None, True],
    description='весь путь',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Охота'], ['start'], ['start']],),
    expected=['ok', None, ['error', 'ValueError', 'нельзя начать квест из статуса active']],
    description='двойной старт',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Поиск'], ['start'], ['finish'], ['start']],),
    expected=['ok', None, None, ['error', 'ValueError', 'нельзя начать квест из статуса done']],
    description='старт после завершения',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Поиск'], ['start'], ['finish'], ['finish'], ['get', 'status']],),
    expected=['ok', None, None, ['error', 'ValueError', 'нельзя завершить квест из статуса done'], 'done'],
    description='двойное завершение',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Поиск'], ['is_done'], ['start'], ['is_done']],),
    expected=['ok', False, None, False],
    description='пока не выполнен',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cl17_quest(actions):
    ...
