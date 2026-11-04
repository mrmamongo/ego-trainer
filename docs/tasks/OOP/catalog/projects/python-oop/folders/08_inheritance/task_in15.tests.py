from ego.testing import case, rules

@rules(
    require_classes=['Employee', 'Manager', 'Intern'],
    require_bases={'Manager': ['Employee'], 'Intern': ['Employee']},
    require_methods={'Employee': ['__init__', 'salary'], 'Manager': ['__init__', 'salary'], 'Intern': ['salary']},
)
@case(
    args=([['Manager', 'Аня', 100, 20], ['Intern', 'Боря', 60], ['Employee', 'Вика', 80]],),
    expected=['Аня: 120', 'Боря: 30', 'Вика: 80'],
    description='три вида сотрудников',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Employee', 'Лев', 50]],),
    expected=['Лев: 50'],
    description='один обычный',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Intern', 'Ира', 41]],),
    expected=['Ира: 20'],
    description='стажёр: нечётный оклад',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected=[],
    description='никого нет',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Manager', 'Юра', 100, 0], ['Manager', 'Мия', 0, 15]],),
    expected=['Юра: 100', 'Мия: 15'],
    description='менеджеры без премии и без оклада',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Intern', 'Тим', 0], ['Employee', 'Зоя', 1], ['Intern', 'Ян', 1]],),
    expected=['Тим: 0', 'Зоя: 1', 'Ян: 0'],
    description='нули и единицы',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_in15_payroll(rows):
    ...
