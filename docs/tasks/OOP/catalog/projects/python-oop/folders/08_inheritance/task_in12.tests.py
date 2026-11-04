from ego.testing import case, rules

@rules(
    require_classes=['Notification', 'Push'],
    require_bases={'Push': ['Notification']},
    require_methods={'Notification': ['__init__', 'send'], 'Push': ['__init__', 'send']},
)
@case(
    args=([['new', 'Push', 'anya', 'chat'], ['get', 'to'], ['get', 'app']],),
    expected=['ok', 'anya', 'chat'],
    description='оба поля на месте',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Push', 'boris', 'mail'], ['send', 'привет']],),
    expected=['ok', 'mail/boris: привет'],
    description='push использует send родителя',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Notification', 'vika'], ['send', 'привет']],),
    expected=['ok', 'vika: привет'],
    description='родитель не сломан',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Push', '', 'app'], ['send', 'x'], ['get', 'to']],),
    expected=['ok', 'app/: x', ''],
    description='пустой адресат',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Push', 'lev', 'game'], ['set', 'to', 'ira'], ['send', 'ход'], ['is', 'Notification']],),
    expected=['ok', 'ok', 'game/ira: ход', True],
    description='адресат поменяли',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_in12_push(actions):
    ...
