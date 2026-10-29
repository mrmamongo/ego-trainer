from ego.testing import case, rules

@rules(
    require_classes=['BankAccount'],
    require_methods={'BankAccount': ['__init__', 'deposit', 'withdraw']},
)
@case(
    args=([['new', 'Аня', 100], ['deposit', 50], ['get', 'balance']],),
    expected=['ok', None, 150],
    description='пополнение',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Боря', 20], ['withdraw', 5], ['get', 'balance']],),
    expected=['ok', None, 15],
    description='снятие',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Вика', 100], ['withdraw', 500], ['get', 'balance']],),
    expected=['ok', ['error', 'ValueError', 'недостаточно денег'], 100],
    description='денег не хватает',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Юра', 10], ['deposit', 0], ['get', 'balance']],),
    expected=['ok', ['error', 'ValueError', 'сумма должна быть больше нуля'], 10],
    description='нулевое пополнение',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Ира', 50], ['withdraw', 50], ['get', 'balance']],),
    expected=['ok', None, 0],
    description='снять всё до копейки',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Лев', 10], ['deposit', -5], ['get', 'owner']],),
    expected=['ok', ['error', 'ValueError', 'сумма должна быть больше нуля'], 'Лев'],
    description='отрицательное пополнение',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Мия', 10], ['deposit', 5], ['withdraw', 15], ['withdraw', 1], ['get', 'balance']],),
    expected=['ok', None, None, ['error', 'ValueError', 'недостаточно денег'], 0],
    description='потратили всё и просим ещё',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cl11_account(actions):
    ...
