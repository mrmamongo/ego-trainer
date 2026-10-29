from ego.testing import case, rules

@rules(
    require_classes=['Money'],
    require_methods={'Money': ['__init__', '__repr__', '__str__']},
)
@case(
    args=([['new', 1250], ['__repr__'], ['__str__']],),
    expected=['ok', 'Money(1250)', '12.50 руб.'],
    description='двенадцать рублей пятьдесят копеек',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 5], ['__str__']],),
    expected=['ok', '0.05 руб.'],
    description='пять копеек: нужен ноль перед пятёркой',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 100], ['__repr__'], ['__str__'], ['get', 'kopecks']],),
    expected=['ok', 'Money(100)', '1.00 руб.', 100],
    description='ровно рубль',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 0], ['__str__']],),
    expected=['ok', '0.00 руб.'],
    description='ноль',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 99999], ['__str__']],),
    expected=['ok', '999.99 руб.'],
    description='почти тысяча',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 100000], ['__repr__'], ['__str__']],),
    expected=['ok', 'Money(100000)', '1000.00 руб.'],
    description='ровно тысяча',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 7], ['__repr__']],),
    expected=['ok', 'Money(7)'],
    description='repr малой суммы',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mg11_money(actions):
    ...
