from ego.testing import case, rules

@rules(
    require_classes=['Player'],
    require_methods={'Player': ['__init__', 'heal']},
)
@case(
    args=([['new', 'Аня', 30], ['heal', 10], ['get', 'hp']],),
    expected=['ok', None, 40],
    description='одно лечение',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Боря', 1], ['heal', 0], ['get', 'hp']],),
    expected=['ok', None, 1],
    description='лечение на ноль',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Вика', 5], ['heal', 3], ['heal', 4], ['get', 'hp']],),
    expected=['ok', None, None, 12],
    description='лечим дважды',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Юра', 0], ['heal', 100], ['get', 'hp']],),
    expected=['ok', None, 100],
    description='с нуля до ста',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Ира', 10], ['heal', 5], ['get', 'name'], ['get', 'hp']],),
    expected=['ok', None, 'Ира', 15],
    description='имя не меняется',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cl04_heal(actions):
    ...
