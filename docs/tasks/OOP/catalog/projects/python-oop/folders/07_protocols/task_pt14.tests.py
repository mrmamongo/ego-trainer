from ego.testing import case, rules

@rules(
    require_functions=['non_empty', 'only_errors'],
)
@case(
    args=('INFO a\nERROR b\nERROR c\n',),
    expected=['ERROR b', 2],
    description='ошибка на второй строке',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('\nINFO a\n\nERROR disk\nINFO z\n',),
    expected=['ERROR disk', 4],
    description='пустые строки пропускаются',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('INFO a\nINFO b\n',),
    expected=['нет ошибок', 2],
    description='ошибок нет: прочитан весь файл',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('',),
    expected=['нет ошибок', 0],
    description='пустой журнал',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('   \n  ERROR x  \n',),
    expected=['ERROR x', 2],
    description='пробелы по краям убираются',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('ERROR first\nERROR second\nERROR third\n',),
    expected=['ERROR first', 1],
    description='ленивость: прочитана одна строка',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pt14_first_error(text):
    ...
