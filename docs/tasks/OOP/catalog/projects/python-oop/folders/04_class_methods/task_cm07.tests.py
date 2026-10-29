from ego.testing import case, rules

@rules(
    require_classes=['Quest'],
    require_methods={'Quest': ['__init__', 'add_tag']},
)
@case(
    args=([['new', 'Волки'], ['add_tag', 'бой'], ['get', 'tags']],),
    expected=['ok', None, ['бой']],
    description='один квест, одна метка',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Волки'], ['add_tag', 'бой'], ['new', 'Лис'], ['get', 'tags']],),
    expected=['ok', None, 'ok', []],
    description='у нового квеста меток нет',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Лис'], ['add_tag', 'хитрость'], ['add_tag', 'лес'], ['get', 'tags']],),
    expected=['ok', None, None, ['хитрость', 'лес']],
    description='две метки подряд',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Дракон'], ['add_tag', 'босс'], ['new', 'Крыса'], ['add_tag', 'подвал'], ['get', 'tags']],),
    expected=['ok', None, 'ok', None, ['подвал']],
    description='метки не перетекают в другой квест',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Тролль'], ['get', 'title'], ['get', 'tags']],),
    expected=['ok', 'Тролль', []],
    description='свежий квест без меток',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cm07_tags(actions):
    ...
