from ego.testing import case, rules

@rules(
    require_classes=['Run'],
    require_decorators={'Run': ['dataclass']},
)
@case(
    args=([[60, 'Аня', ''], [55, 'Вика', ''], [60, 'Боря', 'рекорд']],),
    expected={'names': ['Вика', 'Аня', 'Боря'], 'first_two_equal': False},
    description='время, потом имя',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[60, 'Аня', 'первая'], [60, 'Аня', 'вторая']],),
    expected={'names': ['Аня', 'Аня'], 'first_two_equal': True},
    description='пометка не влияет на равенство',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[10, 'Я', '']],),
    expected={'names': ['Я'], 'first_two_equal': False},
    description='один забег',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected={'names': [], 'first_two_equal': False},
    description='пусто',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[70, 'Боря', ''], [70, 'Аня', ''], [69, 'Вика', '']],),
    expected={'names': ['Вика', 'Аня', 'Боря'], 'first_two_equal': False},
    description='ничья по времени',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[5, 'а', 'x'], [5, 'б', 'x']],),
    expected={'names': ['а', 'б'], 'first_two_equal': False},
    description='разные имена не равны',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[100, 'Аня', 'a'], [100, 'Аня', 'b'], [99, 'Аня', 'c']],),
    expected={'names': ['Аня', 'Аня', 'Аня'], 'first_two_equal': True},
    description='одно имя, разные пометки',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mg16_results(rows):
    ...
