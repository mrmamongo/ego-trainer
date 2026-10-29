from ego.testing import case, rules

@rules(
    require_classes=['Quest'],
    require_decorators={'Quest.title': ['property'], 'Quest.level': ['property'], 'Quest.reward': ['property'], 'Quest.done': ['property']},
    require_methods={'Quest': ['__init__', 'complete']},
)
@case(
    args=([['new', 'Дракон', 100], ['get', 'level'], ['get', 'reward']],),
    expected=['ok', 1, 100],
    description='уровень по умолчанию',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Дракон', 100, 3], ['set', 'level', 5], ['get', 'reward']],),
    expected=['ok', 'ok', 500],
    description='награда следует за уровнем',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Гоблин', 40, 2], ['complete'], ['get', 'done'], ['complete']],),
    expected=['ok', 80, True, ['error', 'ValueError', 'квест уже выполнен']],
    description='квест выполняется один раз',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Крыса', 10], ['get', 'done'], ['get', 'title']],),
    expected=['ok', False, 'Крыса'],
    description='новый квест не выполнен',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Крыса', 10, 0], ['new', 'Крыса', 10, 6], ['new', 'Крыса', 10, 5], ['get', 'reward']],),
    expected=[['error', 'ValueError', 'уровень от 1 до 5'], ['error', 'ValueError', 'уровень от 1 до 5'], 'ok', 50],
    description='уровень проверяется при создании',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Тролль', 30, 2], ['set', 'level', 6], ['set', 'level', 0], ['get', 'level']],),
    expected=['ok', ['error', 'ValueError', 'уровень от 1 до 5'], ['error', 'ValueError', 'уровень от 1 до 5'], 2],
    description='плохой уровень не записывается',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Тролль', 30], ['set', 'reward', 1], ['set', 'done', True], ['set', 'title', 'Эльф'], ['get', 'title']],),
    expected=['ok', ['error', 'AttributeError', ''], ['error', 'AttributeError', ''], ['error', 'AttributeError', ''], 'Тролль'],
    description='награда, статус и название только для чтения',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Тролль', 30], ['set', 'level', 4], ['complete'], ['get', 'reward']],),
    expected=['ok', 'ok', 120, 120],
    description='награда после выполнения',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pr16_quest(actions):
    ...
