from ego.testing import case, rules

@rules(
    require_classes=['ProgressBar'],
    require_methods={'ProgressBar': ['__init__', 'advance']},
)
@case(
    args=([['new', 0], ['get', 'bar'], ['advance', 35], ['get', 'bar']],),
    expected=['ok', '..........', None, '###.......'],
    description='старое: полоса растёт',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 90], ['advance', 100], ['get', 'percent'], ['get', 'bar']],),
    expected=['ok', None, 100, '##########'],
    description='старое: не выше ста',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 30], ['set', 'percent', 80], ['get', 'bar']],),
    expected=['ok', 'ok', '########..'],
    description='новое: полоса следует за percent',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 150], ['new', 100], ['get', 'bar']],),
    expected=[['error', 'ValueError', 'процент от 0 до 100'], 'ok', '##########'],
    description='новое: плохой процент при создании',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 30], ['set', 'percent', -1], ['set', 'percent', 101], ['get', 'percent']],),
    expected=['ok', ['error', 'ValueError', 'процент от 0 до 100'], ['error', 'ValueError', 'процент от 0 до 100'], 30],
    description='новое: плохие значения не записываются',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 30], ['advance', -50], ['get', 'percent']],),
    expected=['ok', ['error', 'ValueError', 'процент от 0 до 100'], 30],
    description='новое: нельзя уйти в минус шагом',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 55], ['get', 'bar'], ['advance', 0], ['get', 'bar']],),
    expected=['ok', '#####.....', None, '#####.....'],
    description='старое: нулевой шаг',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 10], ['set', 'bar', 'хитрость'], ['get', 'bar']],),
    expected=['ok', ['error', 'AttributeError', ''], '#.........'],
    description='новое: bar только для чтения',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pr18_bar(actions):
    ...
