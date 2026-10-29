from ego.testing import case, rules

@rules(
    require_classes=['Player'],
    require_methods={'Player': ['__init__', 'is_alive', 'hit']},
)
@case(
    args=([['new', 10], ['is_alive']],),
    expected=['ok', True],
    description='новый игрок жив',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 10], ['hit', 4], ['get', 'hp']],),
    expected=['ok', True, 6],
    description='удар не смертелен',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 5], ['hit', 5]],),
    expected=['ok', False],
    description='смертельный удар',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 3], ['hit', 1], ['hit', 1], ['hit', 1]],),
    expected=['ok', True, True, False],
    description='три удара',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 1], ['hit', 10], ['is_alive']],),
    expected=['ok', False, False],
    description='после смерти',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cl15_hit(actions):
    ...
