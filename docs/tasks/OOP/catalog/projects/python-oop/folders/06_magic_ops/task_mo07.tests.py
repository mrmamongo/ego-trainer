from ego.testing import case, rules

@rules(
    require_classes=['Inventory'],
    require_methods={'Inventory': ['__init__', '__contains__']},
)
@case(
    args=({'меч': 1, 'зелье': 0, 'щит': 2}, ['меч', 'зелье', 'лук', 'щит']),
    expected=[True, False, False, True],
    description='есть, ноль и нет',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({'меч': 3}, ['меч']),
    expected=[True],
    description='один предмет',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({'яблоко': 5, 'хлеб': 1}, ['хлеб', 'яблоко']),
    expected=[True, True],
    description='все есть',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({}, ['меч']),
    expected=[False],
    description='пустой инвентарь',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({'меч': 1}, []),
    expected=[],
    description='нет запросов',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({'зелье': 0}, ['зелье', 'зелье']),
    expected=[False, False],
    description='ноль дважды',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mo07_has(items, names):
    ...
