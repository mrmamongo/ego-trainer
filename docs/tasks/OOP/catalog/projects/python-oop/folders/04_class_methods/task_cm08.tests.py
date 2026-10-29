from ego.testing import case, rules

@rules(
    require_classes=['Order'],
    require_methods={'Order': ['__init__']},
)
@case(
    args=(['чай', 'кофе'],),
    expected=[2, ['чай', 'кофе']],
    description='два заказа',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['сок'],),
    expected=[1, ['сок']],
    description='один заказ',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected=[0, []],
    description='заказов нет',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['а', 'б', 'в', 'г', 'д'],),
    expected=[5, ['а', 'б', 'в', 'г', 'д']],
    description='пять заказов',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['чай', 'чай'],),
    expected=[2, ['чай', 'чай']],
    description='одинаковые товары считаются отдельно',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cm08_orders(products):
    ...
