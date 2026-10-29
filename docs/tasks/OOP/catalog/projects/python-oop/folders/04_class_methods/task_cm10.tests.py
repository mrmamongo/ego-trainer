from ego.testing import case, rules

@rules(
    require_classes=['Player'],
)
@case(
    args=('Аня:30',),
    expected=['Аня', 30],
    description='имя и здоровье',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('Боря',),
    expected=['Боря', 100],
    description='здоровья нет — берём 100',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('Вика:0',),
    expected=['Вика', 0],
    description='здоровье ноль не заменяется на 100',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('Юра:100',),
    expected=['Юра', 100],
    description='здоровье равно значению по умолчанию',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('Ира:7',),
    expected=['Ира', 7],
    description='однозначное здоровье',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=('Лев',),
    expected=['Лев', 100],
    description='ещё одно имя без здоровья',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_cm10_player_from_text(text):
    ...
