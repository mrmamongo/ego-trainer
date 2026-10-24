from ego.testing import case, rules

@case(
    args=(5, [3, 8, 5, 9]),
    expected=3,
    description='угадал с третьей',
    level="smoke",
)

@case(
    args=(5, [5]),
    expected=1,
    description='угадал сразу',
    level="smoke",
)

@case(
    args=(5, [1, 2, 3]),
    expected=-1,
    description='не угадал ни разу',
    level="smoke",
)

@case(
    args=(5, []),
    expected=-1,
    description='нет попыток',
    level="full",
)

@case(
    args=(5, [5, 5]),
    expected=1,
    description='считаем до первой верной',
    level="full",
)

@case(
    args=(4, [9, 9, 4, 4]),
    expected=3,
    description='две верные подряд',
    level="full",
)

@case(
    args=(-2, [0, -5, -2]),
    expected=3,
    description='отрицательное число',
    level="full",
)

@case(
    args=(10, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
    expected=10,
    description='десятая попытка',
    level="full",
)


@rules(forbid_names=["enumerate"])

def task_mp02_count_tries(secret, guesses):
    ...
