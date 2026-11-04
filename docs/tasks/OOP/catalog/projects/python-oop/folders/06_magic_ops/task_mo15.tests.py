from ego.testing import case, rules

@rules(
    require_classes=['Inventory'],
    require_methods={'Inventory': ['__init__', '__getitem__', '__contains__', '__len__']},
)
@case(
    args=({'меч': 1, 'зелье': 0}, ['меч', 'зелье', 'лук']),
    expected={'kinds': 2, 'rows': [['меч', True, 1], ['зелье', False, 0], ['лук', False, 'KeyError']]},
    description='есть, ноль и нет',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({'яблоко': 5}, ['яблоко']),
    expected={'kinds': 1, 'rows': [['яблоко', True, 5]]},
    description='один предмет',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({}, ['меч']),
    expected={'kinds': 0, 'rows': [['меч', False, 'KeyError']]},
    description='пустой инвентарь',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({'а': 1, 'б': 2, 'в': 0}, []),
    expected={'kinds': 3, 'rows': []},
    description='без запросов',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({'а': 1}, ['а', 'а']),
    expected={'kinds': 1, 'rows': [['а', True, 1], ['а', True, 1]]},
    description='повторный запрос',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=({'щит': 3, 'лук': 0}, ['лук', 'щит', 'стрела']),
    expected={'kinds': 2, 'rows': [['лук', False, 0], ['щит', True, 3], ['стрела', False, 'KeyError']]},
    description='смесь',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mo15_inventory(items, names):
    ...
