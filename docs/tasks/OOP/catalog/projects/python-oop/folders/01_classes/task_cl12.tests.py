from ego.testing import case, rules

@rules(
    require_classes=['Quest'],
    require_methods={'Quest': ['__init__', 'complete']},
)
@case(
    args=([['new', 'Охота'], ['complete'], ['get', 'status']],),
    expected=['ok', None, 'done'],
    description='первое завершение',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Охота'], ['complete'], ['complete']],),
    expected=['ok', None, ['error', 'ValueError', 'квест уже выполнен']],
    description='второе завершение',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Охота'], ['get', 'status']],),
    expected=['ok', 'active'],
    description='квест активен',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Поиск'], ['complete'], ['complete'], ['get', 'status']],),
    expected=['ok', None, ['error', 'ValueError', 'квест уже выполнен'], 'done'],
    description='статус после отказа',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Поиск'], ['complete'], ['complete'], ['complete']],),
    expected=['ok', None, ['error', 'ValueError', 'квест уже выполнен'], ['error', 'ValueError', 'квест уже выполнен']],
    description='отказ повторяется',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cl12_quest(actions):
    ...
