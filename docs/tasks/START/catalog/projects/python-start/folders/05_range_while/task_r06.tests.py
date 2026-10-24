from ego.testing import case

@case(
    args=(6,),
    expected=4,
    description='1, 2, 3, 6',
    level='smoke',
)

@case(
    args=(7,),
    expected=2,
    description='простое число',
    level='smoke',
)

@case(
    args=(12,),
    expected=6,
    description='шесть делителей',
    level='smoke',
)

@case(
    args=(1,),
    expected=1,
    description='у единицы один делитель',
    level='full',
)

@case(
    args=(16,),
    expected=5,
    description='степень двойки',
    level='full',
)

@case(
    args=(36,),
    expected=9,
    description='полный квадрат',
    level='full',
)

@case(
    args=(100,),
    expected=9,
    description='сто',
    level='full',
)
def task_r06_count_divisors(n):
    ...
