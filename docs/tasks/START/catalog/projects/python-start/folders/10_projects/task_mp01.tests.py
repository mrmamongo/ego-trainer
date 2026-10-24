from ego.testing import case

@case(
    args=(7, 3),
    expected='больше',
    description='загаданное больше',
    level="smoke",
)

@case(
    args=(7, 9),
    expected='меньше',
    description='загаданное меньше',
    level="smoke",
)

@case(
    args=(7, 7),
    expected='угадал',
    description='числа равны',
    level="smoke",
)

@case(
    args=(0, -1),
    expected='больше',
    description='отрицательная попытка',
    level="full",
)

@case(
    args=(-5, -5),
    expected='угадал',
    description='отрицательное число угадано',
    level="full",
)

@case(
    args=(100, 99),
    expected='больше',
    description='на единицу меньше',
    level="full",
)

@case(
    args=(100, 101),
    expected='меньше',
    description='на единицу больше',
    level="full",
)

@case(
    args=(1, 1000),
    expected='меньше',
    description='большая попытка',
    level="full",
)

def task_mp01_check_guess(secret, guess):
    ...
