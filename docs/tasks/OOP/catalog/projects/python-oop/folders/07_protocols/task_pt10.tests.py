from ego.testing import case, rules

@case(
    args=('INFO a\nERROR b\nERROR c\n',),
    expected=2,
    description='две ошибки',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('',),
    expected=0,
    description='пустой журнал',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('INFO a\nWARN b\n',),
    expected=0,
    description='ошибок нет',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('ERROR x',),
    expected=1,
    description='одна строка без перевода строки',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('  ERROR отступ\nERROR a\n',),
    expected=1,
    description='с отступом не считается',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('ERROR\nERROR\nERROR\n',),
    expected=3,
    description='все строки ошибки',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pt10_count(text):
    ...
