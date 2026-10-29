from ego.testing import case, rules

@rules(
    require_classes=['Price'],
    require_methods={'Price': ['__init__', 'parse', 'from_text', 'show']},
    require_decorators={'Price.parse': ['staticmethod'], 'Price.from_text': ['classmethod']},
)
@case(
    args=('120 руб',),
    expected=[120, 120, '120 руб'],
    description='простая цена',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('1 250 руб',),
    expected=[1250, 1250, '1250 руб'],
    description='пробел как разделитель тысяч',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('0 руб',),
    expected=[0, 0, '0 руб'],
    description='нулевая цена',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('10 000 руб',),
    expected=[10000, 10000, '10000 руб'],
    description='два разделителя тысяч',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('7руб',),
    expected=[7, 7, '7 руб'],
    description='пробела перед «руб» нет',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('  95 руб ',),
    expected=[95, 95, '95 руб'],
    description='лишние пробелы по краям',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cm16_price(text):
    ...
