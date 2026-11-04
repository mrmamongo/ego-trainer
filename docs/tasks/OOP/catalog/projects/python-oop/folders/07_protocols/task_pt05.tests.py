from ego.testing import case, rules

@rules(
    require_classes=['QuestLog'],
    require_methods={'QuestLog': ['__init__', 'add', '__iter__']},
)
@case(
    args=(['Найти меч', 'Убить дракона'],),
    expected=[['Найти меч', 'Убить дракона'], ['Найти меч', 'Убить дракона']],
    description='два квеста',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['Собрать грибы'],),
    expected=[['Собрать грибы'], ['Собрать грибы']],
    description='один квест',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['а', 'б', 'в'],),
    expected=[['а', 'б', 'в'], ['а', 'б', 'в']],
    description='три квеста',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected=[[], []],
    description='пустой журнал',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=(['а', 'а'],),
    expected=[['а', 'а'], ['а', 'а']],
    description='одинаковые названия остаются',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_pt05_quests(titles):
    ...
