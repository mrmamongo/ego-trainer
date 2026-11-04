from ego.testing import case, rules

@rules(
    require_classes=['Transaction'],
    require_methods={'Transaction': ['__enter__', '__exit__']},
)
@case(
    args=(100, [30, 20]),
    expected=[50, 'ok', True],
    description='всё проходит',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(100, [30, 90]),
    expected=[100, 'ok', True],
    description='нехватка денег: откат, ошибка подавлена',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(100, [30, 0]),
    expected=[100, 'KeyError', False],
    description='KeyError: откат и ошибка наружу',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(50, [60]),
    expected=[50, 'ok', True],
    description='одна слишком большая трата',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(100, []),
    expected=[100, 'ok', True],
    description='трат нет',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(100, [10, 0, 10]),
    expected=[100, 'KeyError', False],
    description='KeyError в середине: откат к началу',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pt18_run(balance, spends):
    ...
