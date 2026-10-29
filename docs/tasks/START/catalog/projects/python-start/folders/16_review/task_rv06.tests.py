from ego.testing import case

@case(
    args=([{'id': 1, 'name': 'Аня'}, {'id': 2, 'name': 'Боря'}], [2, 5, 1]),
    expected=['Боря', '?', 'Аня'],
    description='есть и неизвестные номера',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([{'id': 7, 'name': 'Вика'}], [7]),
    expected=['Вика'],
    description='один пользователь',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([{'id': 1, 'name': 'Аня'}, {'id': 2, 'name': 'Боря'}], [1, 1, 2]),
    expected=['Аня', 'Аня', 'Боря'],
    description='номера повторяются',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([], [1, 2]),
    expected=['?', '?'],
    description='нет пользователей',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([{'id': 1, 'name': 'Аня'}], []),
    expected=[],
    description='нет номеров',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([{'id': 10, 'name': 'Яна'}, {'id': 3, 'name': 'Олег'}, {'id': 8, 'name': 'Ира'}], [8, 99, 3, 99, 10]),
    expected=['Ира', '?', 'Олег', '?', 'Яна'],
    description='порядок по ids, а не по users',
    level="full",
    hide_expected=True,
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([{'id': 0, 'name': 'Админ'}, {'id': 5, 'name': 'Гость'}], [0, 5, -1]),
    expected=['Админ', 'Гость', '?'],
    description='нулевой номер',
    level="full",
    hide_expected=True,
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

def task_rv06_names_by_ids(users, ids):
    ...
