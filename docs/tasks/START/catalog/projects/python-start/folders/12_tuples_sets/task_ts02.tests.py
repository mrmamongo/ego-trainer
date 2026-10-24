from ego.testing import case, rules

@case(
    args=([4, 9, 2, 7],),
    expected=(2, 9),
    description='обычный список',
    level='smoke',
)

@case(
    args=([5],),
    expected=(5, 5),
    description='одно число',
    level='smoke',
)

@case(
    args=([-3, -8, -1],),
    expected=(-8, -1),
    description='все отрицательные',
    level='smoke',
)

@case(
    args=([3, 3, 3],),
    expected=(3, 3),
    description='все равны',
    level='full',
)

@case(
    args=([10, -2, 0, 10],),
    expected=(-2, 10),
    description='повтор наибольшего и ноль',
    level='full',
)

@case(
    args=([1, 2, 3, 4, 5],),
    expected=(1, 5),
    description='по возрастанию',
    level='full',
)

@case(
    args=([9, 7, 4, 1],),
    expected=(1, 9),
    description='по убыванию',
    level='full',
)
@rules(
    forbid_names=['min', 'max', 'sorted'],
    forbid_methods=['sort'],
    messages={'min': 'Наименьшее нужно найти циклом, без min', 'max': 'Наибольшее нужно найти циклом, без max', 'sorted': 'Сортировка здесь не нужна: хватит одного прохода'},
)
def task_ts02_min_max(nums):
    ...
