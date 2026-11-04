from ego.testing import case, rules

@rules(
    require_classes=['Cart'],
    require_methods={'Cart': ['__init__', '__len__', '__getitem__']},
)
@case(
    args=([['чай', 80], ['хлеб', 45]], [0, -1, 'хлеб', 'сыр', 5]),
    expected=['чай', 'хлеб', 45, 'KeyError', 'IndexError'],
    description='номера и названия',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['чай', 80]], [0]),
    expected=['чай'],
    description='старое: номер',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['чай', 80], ['сыр', 300]], ['сыр']),
    expected=[300],
    description='новое: цена по названию',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([], [0, 'чай']),
    expected=['IndexError', 'KeyError'],
    description='пустая корзина',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['чай', 80], ['хлеб', 45]], [-2, -3, 2]),
    expected=['чай', 'IndexError', 'IndexError'],
    description='старое: границы',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['чай', 80]], []),
    expected=[],
    description='без запросов',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mo17_cart(items, keys):
    ...
