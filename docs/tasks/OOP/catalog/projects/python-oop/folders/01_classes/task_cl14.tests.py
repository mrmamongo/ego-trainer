from ego.testing import case, rules

@rules(
    require_classes=['Inventory'],
    require_methods={'Inventory': ['__init__', 'add', 'count', 'total']},
)
@case(
    args=([['new'], ['add', 'меч', 1], ['count', 'меч']],),
    expected=['ok', None, 1],
    description='один предмет',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new'], ['add', 'зелье', 3], ['add', 'зелье', 2], ['count', 'зелье']],),
    expected=['ok', None, None, 5],
    description='количество копится',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new'], ['count', 'щит']],),
    expected=['ok', 0],
    description='предмета нет',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new'], ['add', 'меч', 1], ['add', 'зелье', 4], ['total']],),
    expected=['ok', None, None, 5],
    description='сумма по двум предметам',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new'], ['total']],),
    expected=['ok', 0],
    description='пустой инвентарь',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new'], ['add', 'меч', 2], ['get', 'items']],),
    expected=['ok', None, {'меч': 2}],
    description='словарь в атрибуте items',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cl14_inventory(actions):
    ...
