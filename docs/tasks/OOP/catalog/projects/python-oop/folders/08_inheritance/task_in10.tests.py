from ego.testing import case, rules

@rules(
    require_classes=['Employee', 'Manager'],
    require_bases={'Manager': ['Employee']},
    require_methods={'Employee': ['__init__', 'salary'], 'Manager': ['__init__', 'salary']},
)
@case(
    args=([['new', 'Employee', 'Боря', 100], ['salary']],),
    expected=['ok', 100],
    description='обычный сотрудник',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Manager', 'Аня', 100, 30], ['salary']],),
    expected=['ok', 130],
    description='оклад и премия',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Manager', 'Вика', 80, 0], ['salary'], ['get', 'name']],),
    expected=['ok', 80, 'Вика'],
    description='премии нет',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Manager', 'Лев', 50, 10], ['set', 'base', 70], ['salary']],),
    expected=['ok', 'ok', 80],
    description='оклад поменяли',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['new', 'Manager', 'Ира', 0, 25], ['salary'], ['is', 'Employee']],),
    expected=['ok', 25, True],
    description='нулевой оклад',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_in10_manager(actions):
    ...
