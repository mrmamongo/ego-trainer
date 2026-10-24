from ego.testing import case

@case(
    args=('яблоко', 'груша'),
    expected=(['яблоко'], ['груша']),
    description='две разные корзины',
    level="smoke",
)

@case(
    args=(1, 2),
    expected=([1], [2]),
    description='числа вместо товаров',
    level="smoke",
)

@case(
    args=('a', 'a'),
    expected=(['a'], ['a']),
    description='одинаковые товары, корзины всё равно разные',
    level="smoke",
)

@case(
    args=(0, None),
    expected=([0], [None]),
    description='ноль и None как товары',
    level="full",
)

@case(
    args=('', 'x'),
    expected=([''], ['x']),
    description='пустая строка в первой корзине',
    level="full",
)

@case(
    args=([1], [2]),
    expected=([[1]], [[2]]),
    description='товар сам может быть списком',
    level="full",
)

def task_fd04_two_baskets(first, second):
    ...
