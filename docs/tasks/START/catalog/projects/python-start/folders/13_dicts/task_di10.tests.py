from ego.testing import case

@case(
    args=([{'id': 1, 'name': 'Аня'}, {'id': 2, 'name': 'Боря'}],),
    expected={1: {'id': 1, 'name': 'Аня'}, 2: {'id': 2, 'name': 'Боря'}},
    description='два пользователя',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([{'id': 9, 'name': 'Ира'}],),
    expected={9: {'id': 9, 'name': 'Ира'}},
    description='один пользователь',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected={},
    description='пустой список',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([{'id': 7, 'name': 'Вика'}, {'id': 3, 'name': 'Гена'}, {'id': 5, 'name': 'Даша'}],),
    expected={7: {'id': 7, 'name': 'Вика'}, 3: {'id': 3, 'name': 'Гена'}, 5: {'id': 5, 'name': 'Даша'}},
    description='id идут не по порядку',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([{'id': 'u2', 'name': 'Ева'}, {'id': 'u1', 'name': 'Жора'}],),
    expected={'u2': {'id': 'u2', 'name': 'Ева'}, 'u1': {'id': 'u1', 'name': 'Жора'}},
    description='строковые id',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_di10_index_by_id(users):
    ...
