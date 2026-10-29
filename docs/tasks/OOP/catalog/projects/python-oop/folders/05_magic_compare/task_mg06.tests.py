from ego.testing import case, rules

@rules(
    require_classes=['Message'],
    require_methods={'Message': ['__init__', '__eq__']},
)
@case(
    args=([['Аня', 'привет'], ['Боря', 'привет'], ['Аня', 'привет']],),
    expected=2,
    description='повтор от Ани',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Аня', 'привет']],),
    expected=1,
    description='одно сообщение',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Аня', 'привет'], ['Аня', 'пока']],),
    expected=2,
    description='один автор, разный текст',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected=0,
    description='пусто',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Аня', 'ок'], ['Аня', 'ок'], ['Аня', 'ок']],),
    expected=1,
    description='три одинаковых',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Аня', 'ок'], ['аня', 'ок']],),
    expected=2,
    description='регистр автора важен',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Боря', 'а'], ['Вика', 'б'], ['Боря', 'а'], ['Вика', 'б'], ['Гена', 'а']],),
    expected=3,
    description='перемешанные повторы',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mg06_unique(rows):
    ...
