from ego.testing import case, rules

@rules(
    require_classes=['ShopError', 'OutOfStock', 'PriceError'],
    require_bases={'ShopError': ['Exception'], 'OutOfStock': ['ShopError'], 'PriceError': ['ShopError']},
    require_methods={'OutOfStock': ['__init__'], 'PriceError': ['__init__']},
)
@case(
    args=([['stock', 'меч']],),
    expected=['OutOfStock: нет на складе: меч'],
    description='нет товара',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['price', -5]],),
    expected=['PriceError: цена -5 меньше нуля'],
    description='плохая цена',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['shop', 'сбой'], ['other', 'чужая']],),
    expected=['ShopError: сбой', 'не наша ошибка: чужая'],
    description='общая и чужая ошибки',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected=[],
    description='ошибок нет',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['price', 0], ['stock', ''], ['shop', '']],),
    expected=['PriceError: цена 0 меньше нуля', 'OutOfStock: нет на складе: ', 'ShopError: '],
    description='пустые значения и ноль',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['stock', 'щит'], ['other', 'x'], ['price', -1], ['stock', 'лук']],),
    expected=['OutOfStock: нет на складе: щит', 'не наша ошибка: x', 'PriceError: цена -1 меньше нуля', 'OutOfStock: нет на складе: лук'],
    description='все виды вперемешку',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_in20_errors(rows):
    ...
