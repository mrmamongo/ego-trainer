from ego.testing import case, rules

@rules(
    forbid_names=['Counter'],
    forbid_imports=['collections'],
    messages={
        'Counter': 'Словарь нужно собрать самому, без Counter',
        'collections': 'Модуль collections здесь не нужен',
    },
)
@case(
    args=([[100, 'еда'], [50, 'еда'], [30, 'транспорт']],),
    expected={'еда': {'total': 150, 'count': 2}, 'транспорт': {'total': 30, 'count': 1}},
    description='сумма и количество по двум категориям',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[10, 'кино']],),
    expected={'кино': {'total': 10, 'count': 1}},
    description='одна запись',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([],),
    expected={},
    description='пустой список',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[5, 'а'], [7, 'б'], [3, 'а'], [1, 'б'], [2, 'в']],),
    expected={'а': {'total': 8, 'count': 2}, 'б': {'total': 8, 'count': 2}, 'в': {'total': 2, 'count': 1}},
    description='категории чередуются',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[0, 'еда'], [0, 'еда'], [0, 'еда']],),
    expected={'еда': {'total': 0, 'count': 3}},
    description='нулевые суммы всё равно считаются записями',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[-20, 'возврат'], [100, 'возврат']],),
    expected={'возврат': {'total': 80, 'count': 2}},
    description='старая сумма сохранилась',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_di12_total_by_category(entries):
    ...
