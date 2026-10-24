from ego.testing import case

@case(
    args=(['Аня', 'Боря', 'Вера'], ['Боря', 'Глеб', 'Вера']),
    expected=['Боря', 'Вера'],
    description='два общих имени',
    level='smoke',
)

@case(
    args=(['a', 'b'], ['c', 'd']),
    expected=[],
    description='общих нет',
    level='smoke',
)

@case(
    args=(['x'], ['x']),
    expected=['x'],
    description='одно имя в обоих',
    level='smoke',
)

@case(
    args=([], ['a']),
    expected=[],
    description='первый список пуст',
    level='full',
)

@case(
    args=(['b', 'a', 'b'], ['b', 'b', 'c', 'a']),
    expected=['a', 'b'],
    description='повторы внутри списков',
    level='full',
)

@case(
    args=(['c', 'b', 'a'], ['a', 'b', 'c']),
    expected=['a', 'b', 'c'],
    description='одинаковый набор в разном порядке',
    level='full',
)
def task_ts06_common_friends(a, b):
    ...
