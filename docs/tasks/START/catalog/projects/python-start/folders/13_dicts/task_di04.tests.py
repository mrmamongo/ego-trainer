from ego.testing import case

@case(
    args=({'a': 1, 'b': 2}, 'a', 'x'),
    expected={'x': 1, 'b': 2},
    description='переименовали первый ключ',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({'a': 1, 'b': 2}, 'b', 'x'),
    expected={'a': 1, 'x': 2},
    description='переименовали последний ключ',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({'a': 1}, 'z', 'x'),
    expected={'a': 1},
    description='такого ключа нет',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({}, 'a', 'b'),
    expected={},
    description='пустой словарь',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({'a': 5}, 'a', 'b'),
    expected={'b': 5},
    description='единственная пара',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({'к1': 10, 'к2': 20, 'к3': 30}, 'к2', 'новый'),
    expected={'к1': 10, 'новый': 20, 'к3': 30},
    description='ключ посередине',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
def task_di04_rename_key(d, old, new):
    ...
