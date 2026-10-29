from ego.testing import case, rules

@rules(
    require_classes=['BankAccount'],
    require_decorators={'BankAccount.balance': ['property']},
    require_methods={'BankAccount': ['__init__', 'deposit', 'withdraw']},
)
@case(
    args=([['new', 'Аня', 100], ['set', 'balance', 50], ['get', 'balance']],),
    expected=['ok', 'ok', 50],
    description='присваивание через свойство',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Боря', 10], ['deposit', 5], ['get', 'balance']],),
    expected=['ok', None, 15],
    description='пополнение',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Вика', 20], ['set', 'balance', -1], ['get', 'balance']],),
    expected=['ok', ['error', 'ValueError', 'баланс не может быть отрицательным'], 20],
    description='отрицательный баланс отклонён',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Юра', 30], ['withdraw', 30], ['get', 'balance']],),
    expected=['ok', None, 0],
    description='снять всё до нуля',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Ира', 30], ['withdraw', 31], ['get', 'balance']],),
    expected=['ok', ['error', 'ValueError', 'баланс не может быть отрицательным'], 30],
    description='снять больше, чем есть',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Лев', 5], ['set', 'balance', 0], ['deposit', 7], ['get', 'balance']],),
    expected=['ok', 'ok', None, 7],
    description='ноль допустим',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pr06_account(actions):
    ...
