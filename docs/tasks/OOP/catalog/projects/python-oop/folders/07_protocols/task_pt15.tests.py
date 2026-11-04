from ego.testing import case, rules

@rules(
    require_functions=['transaction'],
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
    description='ошибка на второй трате: откат',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(50, [60]),
    expected=[50, True],
    description='единственная трата слишком велика',
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
def task_pt15_run(balance, spends):
    ...
