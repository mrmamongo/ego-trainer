from ego.testing import case

@case(
    args=(6000,),
    expected=15,
    description='старый вызов: большая сумма',
    level="smoke",
)

@case(
    args=(1200,),
    expected=5,
    description='старый вызов: средняя сумма',
    level="smoke",
)

@case(
    args=(6000, True),
    expected=20,
    description='новый клиент перебивает старое правило',
    level="smoke",
)

@case(
    args=(300, True),
    expected=0,
    description='новый клиент, но сумма мала',
    level="smoke",
)

@case(
    args=(999,),
    expected=0,
    description='старый вызов: граница ниже',
    level="full",
)

@case(
    args=(5000,),
    expected=15,
    description='старый вызов: граница 5000',
    level="full",
    hide_expected=True,
)

@case(
    args=(500, True),
    expected=20,
    description='граница нового правила',
    level="full",
    hide_expected=True,
)

@case(
    args=(499, True),
    expected=0,
    description='ниже границы нового правила',
    level="full",
)

@case(
    args=(1000, False),
    expected=5,
    description='явный False',
    level="full",
    hide_expected=True,
)

@case(
    args=(1500, True),
    expected=20,
    description='новый клиент, средняя сумма',
    level="full",
    hide_expected=True,
)

def task_rv07_discount(total, is_new=False):
    ...
