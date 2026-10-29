from ego.testing import case, rules

@rules(
    require_classes=['Product'],
    require_decorators={'Product.price': ['property'], 'Product.discount': ['property'], 'Product.final_price': ['property']},
    require_methods={'Product': ['__init__']},
)
@case(
    args=([['new', 'Чай', 200, 25], ['get', 'final_price'], ['get', 'price']],),
    expected=['ok', 150, 200],
    description='скидка уменьшает итоговую цену',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Кофе', 300], ['get', 'discount'], ['get', 'final_price']],),
    expected=['ok', 0, 300],
    description='скидка по умолчанию ноль',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Сахар', 100, 10], ['set', 'discount', 150], ['get', 'discount']],),
    expected=['ok', ['error', 'ValueError', 'скидка от 0 до 100'], 10],
    description='слишком большая скидка отклонена',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Мёд', 400, 50], ['set', 'price', 600], ['get', 'final_price']],),
    expected=['ok', 'ok', 300],
    description='итоговая цена пересчитывается',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Мёд', 400, 50], ['set', 'price', 0], ['get', 'price']],),
    expected=['ok', ['error', 'ValueError', 'цена должна быть больше нуля'], 400],
    description='нулевая цена отклонена',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Хлеб', 0], ['new', 'Хлеб', 40, -1], ['new', 'Хлеб', 40, 100], ['get', 'final_price']],),
    expected=[['error', 'ValueError', 'цена должна быть больше нуля'], ['error', 'ValueError', 'скидка от 0 до 100'], 'ok', 0],
    description='проверки работают при создании',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Соль', 0, 150]],),
    expected=[['error', 'ValueError', 'цена должна быть больше нуля']],
    description='две ошибки сразу: сначала проверяется цена',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Рис', 90, 10], ['set', 'final_price', 1], ['get', 'final_price']],),
    expected=['ok', ['error', 'AttributeError', ''], 81],
    description='итоговая цена только для чтения',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pr10_product(actions):
    ...
