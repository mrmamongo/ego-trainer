from ego.testing import case, rules

@rules(
    require_classes=['Message'],
    require_decorators={'Message': ['dataclass']},
)
@case(
    args=([['Аня', 'привет'], ['Боря', 'привет'], ['Аня', 'привет']],),
    expected=[['Аня', 'привет'], ['Боря', 'привет']],
    description='один повтор',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Аня', 'привет']],),
    expected=[['Аня', 'привет']],
    description='одно сообщение',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected=[],
    description='пусто',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Аня', 'ок'], ['Аня', 'ок'], ['Аня', 'ок']],),
    expected=[['Аня', 'ок']],
    description='все одинаковые',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Аня', 'а'], ['Боря', 'б'], ['Аня', 'а'], ['Боря', 'б'], ['Аня', 'в']],),
    expected=[['Аня', 'а'], ['Боря', 'б'], ['Аня', 'в']],
    description='повторы вперемешку, порядок первых',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([['Аня', 'ок'], ['Боря', 'ок']],),
    expected=[['Аня', 'ок'], ['Боря', 'ок']],
    description='одинаковый текст, разные авторы',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mg10_dedupe(rows):
    ...
