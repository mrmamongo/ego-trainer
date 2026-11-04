from ego.testing import case, rules

@rules(
    require_functions=['section'],
)
@case(
    args=('загрузка', False),
    expected=['начало загрузка', 'работа', 'конец загрузка'],
    description='без ошибки',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('загрузка', True),
    expected=['начало загрузка', 'работа', 'конец загрузка', 'ошибка'],
    description='ошибка внутри секции: конец всё равно записан',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('save', False),
    expected=['начало save', 'работа', 'конец save'],
    description='латинское имя',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('x', True),
    expected=['начало x', 'работа', 'конец x', 'ошибка'],
    description='короткое имя и ошибка',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('длинное имя секции', False),
    expected=['начало длинное имя секции', 'работа', 'конец длинное имя секции'],
    description='имя с пробелами',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pt09_section(name, fail):
    ...
