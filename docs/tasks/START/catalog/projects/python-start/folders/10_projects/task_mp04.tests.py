from ego.testing import case

@case(
    args=(5, [1, 2, 3, 5], 3),
    expected=['больше', 'больше', 'больше', 'попытки кончились'],
    description='лишняя попытка не считается',
    level="smoke",
)

@case(
    args=(5, [1, 5, 9], 3),
    expected=['больше', 'угадал'],
    description='угадал внутри лимита',
    level="smoke",
)

@case(
    args=(50, [10, 20, 30, 40, 45, 46, 47, 48]),
    expected=['больше', 'больше', 'больше', 'больше', 'больше', 'больше', 'больше', 'попытки кончились'],
    description='лимит по умолчанию 7',
    level="smoke",
)

@case(
    args=(5, [1, 2, 5], 3),
    expected=['больше', 'больше', 'угадал'],
    description='угадал на последней попытке',
    level="full",
)

@case(
    args=(5, [1, 2], 3),
    expected=['больше', 'больше'],
    description='попытки ещё остались',
    level="full",
)

@case(
    args=(5, [], 3),
    expected=[],
    description='нет попыток',
    level="full",
)

@case(
    args=(5, [9, 9, 9], 3),
    expected=['меньше', 'меньше', 'меньше', 'попытки кончились'],
    description='ровно лимит без победы',
    level="full",
)

@case(
    args=(5, [1, 5], 1),
    expected=['больше', 'попытки кончились'],
    description='одна попытка',
    level="full",
)

@case(
    args=(5, [5, 1], 1),
    expected=['угадал'],
    description='одна попытка и угадал',
    level="full",
)

@case(
    args=(6, [1, 2, 3, 4, 5, 7, 6]),
    expected=['больше', 'больше', 'больше', 'больше', 'больше', 'меньше', 'угадал'],
    description='угадал на седьмой по умолчанию',
    level="full",
)

def task_mp04_game_report(secret, guesses, max_tries=7):
    ...
