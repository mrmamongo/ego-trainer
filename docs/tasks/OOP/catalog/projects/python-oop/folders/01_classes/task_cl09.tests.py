from ego.testing import case, rules

@rules(
    require_classes=['Timer'],
    require_methods={'Timer': ['__init__', 'tick', 'is_over']},
)
@case(
    args=([['new', 3], ['get', 'seconds_left']],),
    expected=['ok', 3],
    description='начальное время',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 2], ['tick'], ['tick'], ['is_over']],),
    expected=['ok', None, None, True],
    description='время вышло',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 2], ['tick'], ['is_over']],),
    expected=['ok', None, False],
    description='ещё идёт',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 1], ['tick'], ['tick'], ['tick'], ['get', 'seconds_left']],),
    expected=['ok', None, None, None, 0],
    description='ниже нуля не уходит',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 0], ['is_over']],),
    expected=['ok', True],
    description='нулевой таймер',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 5], ['is_over'], ['tick'], ['get', 'seconds_left']],),
    expected=['ok', False, None, 4],
    description='один тик',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cl09_timer(actions):
    ...
