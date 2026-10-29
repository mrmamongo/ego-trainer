from ego.testing import case, rules

@rules(
    require_classes=['ShoppingCart'],
    require_methods={'ShoppingCart': ['__init__', 'add', 'total']},
)
@case(
    args=([['new'], ['add', 100], ['add', 50], ['total']],),
    expected=['ok', None, None, 150],
    description='две цены',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new'], ['total']],),
    expected=['ok', 0],
    description='пустая корзина',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new'], ['add', 30], ['total']],),
    expected=['ok', None, 30],
    description='одна цена',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new'], ['add', 10], ['add', 10], ['add', 10], ['add', 10], ['total']],),
    expected=['ok', None, None, None, None, 40],
    description='одинаковые цены',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new'], ['add', 0], ['add', 5], ['total'], ['add', 7], ['total']],),
    expected=['ok', None, None, 5, None, 12],
    description='сумма пересчитывается',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cl16_cart_total(actions):
    ...
