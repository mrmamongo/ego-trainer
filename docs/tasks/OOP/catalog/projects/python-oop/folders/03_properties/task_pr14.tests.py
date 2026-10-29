from ego.testing import case, rules

@rules(
    require_classes=['BankAccount'],
    require_decorators={'BankAccount.owner': ['property'], 'BankAccount.balance': ['property']},
    require_methods={'BankAccount': ['__init__', 'deposit', 'withdraw']},
    forbid_attributes_outside_class=['_balance', '_owner'],
)
@case(
    args=([['new', 'Аня', 100], ['get', 'owner'], ['deposit', 50], ['get', 'balance']],),
    expected=['ok', 'Аня', None, 150],
    description='пополнение',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Боря', 100], ['withdraw', 500], ['get', 'balance']],),
    expected=['ok', ['error', 'ValueError', 'баланс не может быть отрицательным'], 100],
    description='снять больше, чем есть',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Вика', -5], ['new', 'Вика', 5], ['get', 'balance']],),
    expected=[['error', 'ValueError', 'баланс не может быть отрицательным'], 'ok', 5],
    description='отрицательный баланс при создании',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Юра', 20], ['deposit', 0], ['withdraw', -3], ['get', 'balance']],),
    expected=['ok', ['error', 'ValueError', 'сумма должна быть больше нуля'], ['error', 'ValueError', 'сумма должна быть больше нуля'], 20],
    description='сумма должна быть больше нуля',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Ира', 30], ['withdraw', 30], ['get', 'balance'], ['withdraw', 1], ['get', 'balance']],),
    expected=['ok', None, 0, ['error', 'ValueError', 'баланс не может быть отрицательным'], 0],
    description='снять всё до нуля, потом ещё',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Лев', 10], ['set', 'balance', -1], ['set', 'balance', 7], ['get', 'balance']],),
    expected=['ok', ['error', 'ValueError', 'баланс не может быть отрицательным'], 'ok', 7],
    description='присваивание тоже проверяется',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Мия', 1], ['set', 'owner', 'Нина'], ['get', 'owner']],),
    expected=['ok', ['error', 'AttributeError', ''], 'Мия'],
    description='владельца менять нельзя',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Паша', 0], ['get', 'balance']],),
    expected=['ok', 0],
    description='нулевой баланс допустим',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pr14_account(actions):
    ...
