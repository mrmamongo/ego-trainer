from ego.testing import case, rules

@case(
    args=([1, 2, 3],),
    expected=False,
    description='все разные',
    level='smoke',
)

@case(
    args=([1, 2, 1],),
    expected=True,
    description='есть повтор',
    level='smoke',
)

@case(
    args=(['a', 'a'],),
    expected=True,
    description='два одинаковых слова',
    level='smoke',
)

@case(
    args=([],),
    expected=False,
    description='пустой список',
    level='full',
)

@case(
    args=([5],),
    expected=False,
    description='один элемент',
    level='full',
)

@case(
    args=(['a', 'A'],),
    expected=False,
    description='регистр различается',
    level='full',
)

@case(
    args=([7, 7, 7, 7],),
    expected=True,
    description='все одинаковые',
    level='full',
)
@rules(
    forbid_nodes=['For', 'While'],
    forbid_methods=['count', 'index'],
    messages={'For': 'Цикл не нужен: сравни len(set(items)) и len(items)', 'While': 'Цикл не нужен: сравни len(set(items)) и len(items)'},
)
def task_ts08_has_duplicates(items):
    ...
