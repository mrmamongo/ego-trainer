from ego.testing import case, rules

@case(
    args=(4,),
    expected=[1, 2, 4, 8],
    description='четыре степени',
    level='smoke',
)

@case(
    args=(1,),
    expected=[1],
    description='только единица',
    level='smoke',
)

@case(
    args=(3,),
    expected=[1, 2, 4],
    description='три степени',
    level='smoke',
)

@case(
    args=(0,),
    expected=[],
    description='ноль степеней',
    level='full',
)

@case(
    args=(8,),
    expected=[1, 2, 4, 8, 16, 32, 64, 128],
    description='восемь степеней',
    level='full',
)

@case(
    args=(11,),
    expected=[1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024],
    description='одиннадцать степеней',
    level='full',
)


@rules(
    forbid_nodes=["Pow"],
    messages={"Pow": "Оператор ** использовать нельзя: умножай предыдущую степень на 2"},
)

def task_r11_powers_of_two(k):
    ...
