from ego.testing import case, rules

@rules(
    require_classes=['Item'],
    require_decorators={'Item': ['dataclass']},
)
@case(
    args=([{'name': 'Меч', 'qty': 2, 'price': 100}, {'name': 'Щит', 'qty': 1, 'price': 50}, {'name': 'Зелье', 'qty': 5, 'price': 10}], 0),
    expected=300,
    description='считаем все товары',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([{'name': 'Меч', 'qty': 2, 'price': 100}, {'name': 'Щит', 'qty': 1, 'price': 50}, {'name': 'Зелье', 'qty': 5, 'price': 10}], 50),
    expected=250,
    description='только товары от 50',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([], 10),
    expected=0,
    description='пустой склад',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([{'name': 'Меч', 'qty': 2, 'price': 100}, {'name': 'Щит', 'qty': 1, 'price': 50}, {'name': 'Зелье', 'qty': 5, 'price': 10}], 100),
    expected=200,
    description='цена ровно на границе входит',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([{'name': 'Меч', 'qty': 2, 'price': 100}, {'name': 'Щит', 'qty': 1, 'price': 50}, {'name': 'Зелье', 'qty': 5, 'price': 10}], 101),
    expected=0,
    description='ни один товар не подходит',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([{'name': 'Лук', 'qty': 0, 'price': 30}, {'name': 'Стрела', 'qty': 20, 'price': 3}], 1),
    expected=60,
    description='нулевой запас ничего не добавляет',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_dc08_stock_value(rows, min_price):
    ...
