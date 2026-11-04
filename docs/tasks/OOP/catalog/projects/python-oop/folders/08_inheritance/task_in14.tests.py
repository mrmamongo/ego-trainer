from ego.testing import case, rules

@rules(
    require_functions=['task_in14_fees'],
)
@case(
    args=(['Cash', 'Card', 'Crypto'], 1000),
    expected={'Cash': 0, 'Card': 20, 'Crypto': 11},
    description='три способа',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['Card'], 250),
    expected={'Card': 5},
    description='только карта',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['Crypto', 'Cash'], 99),
    expected={'Crypto': 1, 'Cash': 0},
    description='маленькая сумма',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([], 500),
    expected={},
    description='пустой список способов',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['Card', 'Crypto'], 0),
    expected={'Card': 0, 'Crypto': 1},
    description='нулевая сумма',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['Card', 'Card'], 100),
    expected={'Card': 2},
    description='повтор способа не плодит ключи',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_in14_fees(kinds, amount):
    ...
