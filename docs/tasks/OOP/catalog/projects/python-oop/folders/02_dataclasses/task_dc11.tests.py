from ego.testing import case, rules

@rules(
    require_classes=['Profile'],
    require_decorators={'Profile': ['dataclass']},
    require_methods={'Profile': ['describe']},
)
@case(
    args=([['new', 'Аня'], ['describe'], ['get', 'level']],),
    expected=['ok', 'Аня, уровень 1', 1],
    description='уровень по умолчанию',
    level='smoke',
    comparison='value',
)
@case(
    args=([['new', 'Боря', 5], ['describe']],),
    expected=['ok', 'Боря, уровень 5'],
    description='уровень передали',
    level='smoke',
    comparison='value',
)
@case(
    args=([['new', 'Аня'], ['set', 'level', 9]],),
    expected=['ok', ['error', 'FrozenInstanceError', "cannot assign to field 'level'"]],
    description='поле level менять нельзя',
    level='smoke',
    comparison='value',
)
@case(
    args=([['new', 'Вика', 3], ['set', 'name', 'Ира'], ['get', 'name']],),
    expected=['ok', ['error', 'FrozenInstanceError', "cannot assign to field 'name'"], 'Вика'],
    description='поле name менять нельзя, значение осталось',
    level='full',
    comparison='value',
)
@case(
    args=([['new', 'Аня', 2], ['set', 'level', 3], ['describe']],),
    expected=['ok', ['error', 'FrozenInstanceError', "cannot assign to field 'level'"], 'Аня, уровень 2'],
    description='после неудачной записи describe прежний',
    level='full',
    comparison='value',
)
@case(
    args=([['new', 'Нулевой', 0], ['describe']],),
    expected=['ok', 'Нулевой, уровень 0'],
    description='уровень 0 — тоже значение',
    level='full',
    comparison='value',
)
def task_dc11_profile(actions):
    ...
