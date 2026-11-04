from ego.testing import case, rules

@rules(
    require_classes=['Cart'],
    require_methods={'Cart': ['__init__', '__len__', '__bool__']},
)
@case(
    args=([['чай', 80], ['пакет', 0]],),
    expected=[True, 2, 'есть что оплатить'],
    description='платный и бесплатный',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected=[False, 0, 'нечего оплачивать'],
    description='пустая корзина',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['пакет', 0]],),
    expected=[False, 1, 'нечего оплачивать'],
    description='только бесплатное',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['хлеб', 45]],),
    expected=[True, 1, 'есть что оплатить'],
    description='один платный',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['пакет', 0], ['наклейка', 0]],),
    expected=[False, 2, 'нечего оплачивать'],
    description='всё бесплатное',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['чай', 80], ['хлеб', 45], ['сыр', 300]],),
    expected=[True, 3, 'есть что оплатить'],
    description='три товара',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mo16_cart(items):
    ...
