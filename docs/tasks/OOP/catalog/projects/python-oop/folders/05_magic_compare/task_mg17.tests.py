from ego.testing import case, rules

@rules(
    require_classes=['Book'],
    require_methods={'Book': ['__init__', '__lt__']},
)
@case(
    args=([['Дюна', 1965], ['Солярис', 1961]],),
    expected=['Солярис', 'Дюна'],
    description='старое поведение: по году',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Б', 2000], ['А', 2000]],),
    expected=['А', 'Б'],
    description='новое: при равном годе по названию',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Книга', 1999]],),
    expected=['Книга'],
    description='одна книга',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected=[],
    description='пусто',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Б', 2000], ['В', 1999], ['А', 2000]],),
    expected=['В', 'А', 'Б'],
    description='смесь лет и ничьих',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Я', 1990], ['Б', 1990], ['А', 1990]],),
    expected=['А', 'Б', 'Я'],
    description='все годы равны',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Борис', 2010], ['Анна', 2011], ['Вера', 2010]],),
    expected=['Борис', 'Вера', 'Анна'],
    description='две книги одного года среди других',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mg17_shelf(rows):
    ...
