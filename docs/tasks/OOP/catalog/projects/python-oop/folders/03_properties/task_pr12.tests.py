from ego.testing import case, rules

@rules(
    require_classes=['Account'],
    require_decorators={'Account.balance': ['property']},
    require_functions=['apply_change'],
)
@case(
    args=(100, [-30, -100, 50, -120]),
    expected={'results': [True, False, True, True], 'balance': 0},
    description='отказ посередине, потом снова можно',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(50, [20, 30]),
    expected={'results': [True, True], 'balance': 100},
    description='только пополнения',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(10, [-11]),
    expected={'results': [False], 'balance': 10},
    description='нельзя уйти в минус',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(0, [-1]),
    expected={'results': [False], 'balance': 0},
    description='минус с нулевого баланса',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(5, []),
    expected={'results': [], 'balance': 5},
    description='изменений нет',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(40, [-40, 0, -1]),
    expected={'results': [True, True, False], 'balance': 0},
    description='ровно в ноль и нулевое изменение',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(20, [-5, -5, -5, -5, -5]),
    expected={'results': [True, True, True, True, False], 'balance': 0},
    description='постепенно до нуля',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pr12_change(start, deltas):
    ...
