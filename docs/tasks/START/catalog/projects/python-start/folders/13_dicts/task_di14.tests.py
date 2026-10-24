from ego.testing import case

@case(
    args=([{'name': 'Аня', 'level': 3, 'active': True}, {'name': 'Боря', 'level': 1, 'active': False}, {'name': 'Вика', 'level': 2, 'active': True}],),
    expected=['Аня', 'Вика'],
    description='двое активных',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([{'name': 'Боря', 'level': 1, 'active': False}],),
    expected=[],
    description='нет активных',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected=[],
    description='пустой список',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([{'name': 'Ира', 'level': 5, 'active': True}],),
    expected=['Ира'],
    description='один активный',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([{'name': 'я', 'level': 0, 'active': True}, {'name': 'ты', 'level': 0, 'active': True}, {'name': 'он', 'level': 0, 'active': False}, {'name': 'мы', 'level': 0, 'active': True}],),
    expected=['я', 'ты', 'мы'],
    description='порядок сохраняется',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_di14_active_names(users):
    ...
