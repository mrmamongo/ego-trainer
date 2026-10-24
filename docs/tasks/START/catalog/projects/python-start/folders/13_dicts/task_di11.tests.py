from ego.testing import case, rules

@rules(
    forbid_names=['Counter'],
    forbid_methods=['setdefault'],
    forbid_imports=['collections'],
    messages={
        'Counter': 'Словарь нужно собрать самому, без Counter',
        'setdefault': 'Начальное значение бери через get, setdefault не нужен',
        'collections': 'Модуль collections здесь не нужен',
    },
)
@case(
    args=([[100, 'еда'], [50, 'еда'], [30, 'транспорт']],),
    expected={'еда': 150, 'транспорт': 30},
    description='две категории',
    level='smoke',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[10, 'кино']],),
    expected={'кино': 10},
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
    expected={'а': 8, 'б': 8, 'в': 2},
    description='категории чередуются',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[0, 'еда'], [0, 'еда']],),
    expected={'еда': 0},
    description='нулевые суммы',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
@case(
    args=([[-20, 'возврат'], [100, 'возврат']],),
    expected={'возврат': 80},
    description='отрицательная сумма',
    level='full',
    comparison='value',
    check_inputs_unchanged=True,
)
def task_di11_total_by_category(entries):
    ...
