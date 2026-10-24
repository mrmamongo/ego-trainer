from ego.testing import case

@case(
    args=(5, [3, 8, 5, 9]),
    expected=['больше', 'меньше', 'угадал'],
    description='после верной есть ещё попытка',
    level="smoke",
)

@case(
    args=(5, [1, 2]),
    expected=['больше', 'больше'],
    description='не угадал',
    level="smoke",
)

@case(
    args=(5, [5, 1]),
    expected=['угадал'],
    description='угадал с первой',
    level="smoke",
)

@case(
    args=(5, []),
    expected=[],
    description='нет попыток',
    level="full",
)

@case(
    args=(5, [9]),
    expected=['меньше'],
    description='одна неверная',
    level="full",
)

@case(
    args=(5, [6, 5, 5]),
    expected=['меньше', 'угадал'],
    description='верная повторена',
    level="full",
)

@case(
    args=(0, [-3, 3, 0]),
    expected=['больше', 'меньше', 'угадал'],
    description='ноль и отрицательные',
    level="full",
)

def task_mp03_game_report(secret, guesses):
    ...
