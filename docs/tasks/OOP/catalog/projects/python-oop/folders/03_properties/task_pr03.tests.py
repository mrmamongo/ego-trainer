from ego.testing import case, rules

@rules(
    require_classes=['Product'],
    require_decorators={'Product.name': ['property'], 'Product.price': ['property']},
    require_methods={'Product': ['__init__', 'describe']},
)
@case(
    args=([['new', 'Чай', 120], ['get', 'name'], ['get', 'price']],),
    expected=['ok', 'Чай', 120],
    description='поля читаются',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Кофе', 300], ['describe']],),
    expected=['ok', 'Кофе: 300'],
    description='describe собирает строку',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Сахар', 0], ['get', 'price']],),
    expected=['ok', 0],
    description='нулевая цена',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Чай', 120], ['set', 'price', 50], ['get', 'price']],),
    expected=['ok', ['error', 'AttributeError', ''], 120],
    description='цену присвоить нельзя',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Чай', 120], ['set', 'name', 'Кофе'], ['describe']],),
    expected=['ok', ['error', 'AttributeError', ''], 'Чай: 120'],
    description='имя присвоить нельзя',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Мёд', 450], ['get', 'name'], ['get', 'price'], ['describe']],),
    expected=['ok', 'Мёд', 450, 'Мёд: 450'],
    description='всё вместе',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pr03_product(actions):
    ...
