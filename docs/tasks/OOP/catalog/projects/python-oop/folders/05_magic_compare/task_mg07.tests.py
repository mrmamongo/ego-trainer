from ego.testing import case, rules

@rules(
    require_classes=['Ticket'],
    require_methods={'Ticket': ['__init__', '__lt__']},
)
@case(
    args=([[2, 2], [1, 2], [3, 1]],),
    expected=[1, 2, 3],
    description='равные приоритеты идут по номеру',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[5, 1], [4, 1]],),
    expected=[4, 5],
    description='два тикета с одним приоритетом',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[1, 1], [2, 3], [3, 2]],),
    expected=[2, 3, 1],
    description='разные приоритеты',
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
    args=([[7, 2]],),
    expected=[7],
    description='один тикет',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[3, 2], [2, 2], [1, 2]],),
    expected=[1, 2, 3],
    description='все приоритеты равны',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[9, 1], [8, 3], [7, 3], [6, 2], [5, 2]],),
    expected=[7, 8, 5, 6, 9],
    description='несколько групп',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_mg07_queue(rows):
    ...
