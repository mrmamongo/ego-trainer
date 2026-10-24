from ego.testing import case, rules

@rules(
    forbid_methods=['sort'],
    messages={
        'sort': 'sort меняет список на месте; используй sorted, он возвращает новый',
    },
)
@case(
    args=([{'name': 'Вика', 'level': 2}, {'name': 'Гена', 'level': 3}, {'name': 'Боря', 'level': 2}, {'name': 'Аня', 'level': 3}],),
    expected=[{'name': 'Аня', 'level': 3}, {'name': 'Гена', 'level': 3}, {'name': 'Боря', 'level': 2}, {'name': 'Вика', 'level': 2}],
    description='уровни по убыванию, имена по алфавиту',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([{'name': 'Ира', 'level': 1}],),
    expected=[{'name': 'Ира', 'level': 1}],
    description='один пользователь',
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
    args=([{'name': 'а', 'level': 1}, {'name': 'б', 'level': 2}, {'name': 'в', 'level': 3}],),
    expected=[{'name': 'в', 'level': 3}, {'name': 'б', 'level': 2}, {'name': 'а', 'level': 1}],
    description='все разные уровни',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([{'name': 'я', 'level': 5}, {'name': 'а', 'level': 5}, {'name': 'м', 'level': 5}],),
    expected=[{'name': 'а', 'level': 5}, {'name': 'м', 'level': 5}, {'name': 'я', 'level': 5}],
    description='все уровни равны',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_di23_sort_users(users):
    ...
