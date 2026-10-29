from ego.testing import case, rules

@rules(
    require_classes=['BankAccount'],
    require_methods={'BankAccount': ['__init__', 'deposit', 'withdraw']},
    forbid_attributes_outside_class=['_balance'],
)
@case(
    args=([['new', 'Аня', 100], ['deposit', 50], ['get', 'balance']],),
    expected=['ok', None, 150],
    description='старое: пополнение',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Боря', 20], ['withdraw', 500], ['get', 'balance']],),
    expected=['ok', ['error', 'ValueError', 'недостаточно денег'], 20],
    description='старое: денег не хватает',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Вика', 10], ['set', 'balance', -5], ['get', 'balance']],),
    expected=['ok', ['error', 'ValueError', 'баланс не может быть отрицательным'], 10],
    description='новое: присваивание в минус отклонено',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Юра', -1], ['new', 'Юра', 0], ['get', 'balance']],),
    expected=[['error', 'ValueError', 'баланс не может быть отрицательным'], 'ok', 0],
    description='новое: отрицательный баланс при создании',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Ира', 100], ['deposit', -500], ['get', 'balance']],),
    expected=['ok', ['error', 'ValueError', 'баланс не может быть отрицательным'], 100],
    description='новое: отрицательное пополнение уводит в минус',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Лев', 40], ['withdraw', 40], ['get', 'balance'], ['withdraw', 1]],),
    expected=['ok', None, 0, ['error', 'ValueError', 'недостаточно денег']],
    description='старое: снять всё и ещё',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Мия', 5], ['set', 'balance', 0], ['set', 'balance', 70], ['withdraw', 20], ['get', 'balance']],),
    expected=['ok', 'ok', 'ok', None, 50],
    description='новое: присваивание допустимых значений',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Паша', 10], ['get', 'owner'], ['set', 'owner', 'Нина'], ['get', 'owner']],),
    expected=['ok', 'Паша', 'ok', 'Нина'],
    description='владелец по-прежнему обычный атрибут',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pr17_account(actions):
    ...
