from ego.testing import case, rules

@rules(
    require_functions=['log_calls'],
)
@case(
    args=(['Аня', 'Боря'],),
    expected=[['Привет, Аня!', 'Привет, Боря!'], [['Аня'], ['Боря']]],
    description='два вызова, журнал по порядку',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['Вика'],),
    expected=[['Привет, Вика!'], [['Вика']]],
    description='один вызов',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected=[[], []],
    description='вызовов не было, журнал пустой',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['Юра', 'Юра', 'Юра'],),
    expected=[['Привет, Юра!', 'Привет, Юра!', 'Привет, Юра!'], [['Юра'], ['Юра'], ['Юра']]],
    description='одинаковые вызовы пишутся каждый раз',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['Ира', 'Лев', 'Мия', 'Ян'],),
    expected=[['Привет, Ира!', 'Привет, Лев!', 'Привет, Мия!', 'Привет, Ян!'], [['Ира'], ['Лев'], ['Мия'], ['Ян']]],
    description='четыре вызова',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cm05_log(names):
    ...
