from ego.testing import case, rules

@rules(
    require_classes=['Message'],
    require_methods={'Message': ['__init__', '__eq__', '__hash__']},
)
@case(
    args=([['Аня', 'привет'], ['Боря', 'привет'], ['Аня', 'привет']],),
    expected={'count': 2, 'first_seen': [['Аня', 'привет'], ['Боря', 'привет']]},
    description='повтор от Ани',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Аня', 'привет'], ['Аня', 'пока']],),
    expected={'count': 2, 'first_seen': [['Аня', 'привет'], ['Аня', 'пока']]},
    description='один автор, разный текст',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Аня', 'привет']],),
    expected={'count': 1, 'first_seen': [['Аня', 'привет']]},
    description='одно сообщение',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected={'count': 0, 'first_seen': []},
    description='пусто',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Аня', 'ок'], ['Аня', 'ок'], ['Аня', 'ок']],),
    expected={'count': 1, 'first_seen': [['Аня', 'ок']]},
    description='три одинаковых',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Аня', 'а'], ['Боря', 'б'], ['Аня', 'а'], ['Боря', 'в'], ['Боря', 'б']],),
    expected={'count': 3, 'first_seen': [['Аня', 'а'], ['Боря', 'б'], ['Боря', 'в']]},
    description='порядок первых вхождений',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Аня', 'ок'], ['аня', 'ок']],),
    expected={'count': 2, 'first_seen': [['Аня', 'ок'], ['аня', 'ок']]},
    description='регистр автора важен',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mg15_dedupe(rows):
    ...
