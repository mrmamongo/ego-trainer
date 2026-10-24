from ego.testing import case

@case(
    args=(['Аня', 'Боря', 'Вера'], ['Боря', 'Глеб']),
    expected=['Аня', 'Вера'],
    description='часть имён только в первом',
    level='smoke',
)

@case(
    args=(['a', 'b'], ['b', 'a']),
    expected=[],
    description='всё есть во втором',
    level='smoke',
)

@case(
    args=(['a', 'b'], []),
    expected=['a', 'b'],
    description='второй список пуст',
    level='smoke',
)

@case(
    args=([], ['a']),
    expected=[],
    description='первый список пуст',
    level='full',
)

@case(
    args=(['c', 'a', 'c'], ['b']),
    expected=['a', 'c'],
    description='повторы и сортировка',
    level='full',
)

@case(
    args=(['x', 'y'], ['z']),
    expected=['x', 'y'],
    description='ничего общего',
    level='full',
)
def task_ts07_only_in_first(a, b):
    ...
