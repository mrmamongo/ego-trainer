from ego.testing import case

@case(
    args=(['pear', 'apple', 'pear', 'fig'],),
    expected=['apple', 'fig', 'pear'],
    description='есть повтор',
    level='smoke',
)

@case(
    args=(['b', 'a', 'b'],),
    expected=['a', 'b'],
    description='две буквы с повтором',
    level='smoke',
)

@case(
    args=(['x'],),
    expected=['x'],
    description='одно слово',
    level='smoke',
)

@case(
    args=([],),
    expected=[],
    description='пустой список',
    level='full',
)

@case(
    args=(['z', 'z', 'z'],),
    expected=['z'],
    description='все одинаковые',
    level='full',
)

@case(
    args=(['b', 'B', 'a'],),
    expected=['B', 'a', 'b'],
    description='заглавные идут раньше строчных',
    level='full',
)
def task_ts05_unique_sorted(words):
    ...
