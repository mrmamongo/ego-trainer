from ego.testing import case

@case(
    args=({'яблоки': 5}, 'яблоки', 3),
    expected={'яблоки': 8},
    description='товар уже есть',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({'яблоки': 5}, 'груши', 2),
    expected={'яблоки': 5, 'груши': 2},
    description='новый товар',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({}, 'чай', 1),
    expected={'чай': 1},
    description='пустой склад',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({'а': 1, 'б': 2, 'в': 3}, 'б', 10),
    expected={'а': 1, 'б': 12, 'в': 3},
    description='остальные товары не затронуты',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({'а': 0}, 'а', 4),
    expected={'а': 4},
    description='было ноль',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
def task_di16_inventory_add(inventory, item, qty):
    ...
