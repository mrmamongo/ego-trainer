from ego.testing import case, rules

@case(
    args=(['a', 'b', 'a', 'b'],),
    expected='a',
    description='повторяется первое слово',
    level='smoke',
)

@case(
    args=(['a', 'b', 'c'],),
    expected='',
    description='повторов нет',
    level='smoke',
)

@case(
    args=(['x', 'y', 'y', 'x'],),
    expected='y',
    description='раньше обнаружен повтор y',
    level='smoke',
)

@case(
    args=(['k', 'k'],),
    expected='k',
    description='повтор сразу',
    level='full',
)

@case(
    args=([],),
    expected='',
    description='пустой список',
    level='full',
)

@case(
    args=(['a', 'b', 'c', 'b', 'a'],),
    expected='b',
    description='повтор b обнаружен раньше повтора a',
    level='full',
)

@case(
    args=(['one', 'two', 'three', 'four', 'three'],),
    expected='three',
    description='повтор в конце',
    level='full',
)
@rules(
    forbid_nodes=['List'],
    forbid_names=['list'],
    forbid_methods=['count', 'index'],
    messages={'List': 'Увиденное храни в множестве set(), а не в списке', 'list': 'Увиденное храни в множестве set(), а не в списке'},
)
def task_ts09_first_repeat(items):
    ...
