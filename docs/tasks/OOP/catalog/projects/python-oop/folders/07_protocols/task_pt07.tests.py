from ego.testing import case, rules

@rules(
    require_classes=['Transaction'],
    require_methods={'Transaction': ['__enter__', '__exit__']},
)
@case(
    args=(100, [30, 20]),
    expected=[50, False],
    description='обе траты проходят',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(100, [30, 90]),
    expected=[100, True],
    description='вторая трата с ошибкой: откат и ошибка наружу',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(50, [60]),
    expected=[50, True],
    description='одна слишком большая трата',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(100, []),
    expected=[100, False],
    description='трат нет',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(100, [100]),
    expected=[0, False],
    description='ровно весь баланс',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(100, [40, 40, 40]),
    expected=[100, True],
    description='ошибка на третьей трате: откат к началу',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pt07_run(balance, spends):
    ...
