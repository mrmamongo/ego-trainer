from ego.testing import case, rules

@case(
    args=(5,),
    expected=8,
    description='между 4 и 8',
    level='smoke',
)

@case(
    args=(9,),
    expected=16,
    description='между 8 и 16',
    level='smoke',
)

@case(
    args=(8,),
    expected=8,
    description='ровно степень двойки',
    level='smoke',
)

@case(
    args=(1,),
    expected=1,
    description='единица',
    level='full',
)

@case(
    args=(2,),
    expected=2,
    description='двойка',
    level='full',
)

@case(
    args=(3,),
    expected=4,
    description='тройка',
    level='full',
)

@case(
    args=(1000,),
    expected=1024,
    description='тысяча',
    level='full',
)

@case(
    args=(1024,),
    expected=1024,
    description='ровно 1024',
    level='full',
)

@case(
    args=(1025,),
    expected=2048,
    description='на единицу больше 1024',
    level='full',
)


@rules(
    forbid_imports=["math"],
    forbid_nodes=["Pow"],
    messages={
        "Pow": "Оператор ** использовать нельзя: умножай на 2 в цикле while",
        "math": "Модуль math использовать нельзя: умножай на 2 в цикле while",
    },
)

def task_r20_power_of_two_at_least(n):
    ...
