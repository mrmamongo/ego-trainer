from ego.testing import case

@case(
    args=({'яблоки': 5, 'груши': 2}, ['яблоки', 'груши']),
    expected=7,
    description='все товары есть',
    level='smoke',
    check_inputs_unchanged=True,
)
@case(
    args=({'яблоки': 5}, ['яблоки', 'киви']),
    expected=5,
    description='одного товара нет',
    level='smoke',
    check_inputs_unchanged=True,
)
@case(
    args=({}, []),
    expected=0,
    description='пусто',
    level='smoke',
    check_inputs_unchanged=True,
)
@case(
    args=({'груши': 2}, ['груши', 'груши', 'груши']),
    expected=6,
    description='повторы считаются каждый раз',
    level='full',
    check_inputs_unchanged=True,
)
@case(
    args=({'яблоки': 5}, ['киви', 'слива']),
    expected=0,
    description='ни одного нет',
    level='full',
    check_inputs_unchanged=True,
)
@case(
    args=({}, ['чай']),
    expected=0,
    description='пустой склад',
    level='full',
    check_inputs_unchanged=True,
)
@case(
    args=({'яблоки': 0, 'груши': 4}, ['яблоки', 'груши']),
    expected=4,
    description='нулевое количество',
    level='full',
    check_inputs_unchanged=True,
)
def task_di03_total_stock(stock, items):
    ...
