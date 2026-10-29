from ego.testing import case, rules

@rules(
    require_classes=['ShoppingCart'],
    require_methods={'ShoppingCart': ['__init__', 'add', 'count', 'total', 'summary']},
)
@case(
    args=([['new'], ['add', 'хлеб', 50], ['total']],),
    expected=['ok', None, 50],
    description='один товар',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new'], ['add', 'хлеб', 50, 2], ['add', 'чай', 30], ['count']],),
    expected=['ok', None, None, 3],
    description='штуки считаются',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new'], ['summary']],),
    expected=['ok', '0 шт. на 0'],
    description='пустая корзина',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new'], ['add', 'хлеб', 50, 2], ['add', 'чай', 30], ['summary']],),
    expected=['ok', None, None, '3 шт. на 130'],
    description='сводка',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new'], ['add', 'сок', 80, 3], ['total'], ['count']],),
    expected=['ok', None, 240, 3],
    description='цена на количество',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new'], ['add', 'сок', 10], ['add', 'сок', 10], ['count'], ['total']],),
    expected=['ok', None, None, 2, 20],
    description='одинаковые товары',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cl18_cart(actions):
    ...
