from ego.testing import case, rules

@case(
    args=([{'name': 'Боря', 'score': 50}, {'name': 'Аня', 'score': 50}, {'name': 'Вика', 'score': 40}],),
    expected='Аня',
    description='ничья: побеждает имя раньше по алфавиту',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=([{'name': 'Аня', 'score': 10}, {'name': 'Боря', 'score': 30}, {'name': 'Вика', 'score': 20}],),
    expected='Боря',
    description='лучший в середине',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=([{'name': 'Вика', 'score': 7}],),
    expected='Вика',
    description='один игрок',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=([],),
    expected=None,
    description='пустой список',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=([{'name': 'Яна', 'score': -3}, {'name': 'Олег', 'score': -1}, {'name': 'Ира', 'score': -1}],),
    expected='Ира',
    description='отрицательные счета и ничья',
    level="full",
    hide_expected=True,
    check_inputs_unchanged=True,
)

@case(
    args=([{'name': 'Вика', 'score': 7}, {'name': 'Аня', 'score': 7}, {'name': 'Боря', 'score': 7}],),
    expected='Аня',
    description='ничья у всех',
    level="full",
    hide_expected=True,
    check_inputs_unchanged=True,
)

@case(
    args=([{'name': 'Аня', 'score': 1}, {'name': 'Боря', 'score': 2}, {'name': 'Вика', 'score': 3}],),
    expected='Вика',
    description='лучший последний',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=([{'name': 'Яна', 'score': 9}, {'name': 'Аня', 'score': 9}, {'name': 'Боря', 'score': 9}, {'name': 'Вика', 'score': 12}],),
    expected='Вика',
    description='ничья не у лучшего',
    level="full",
    hide_expected=True,
    check_inputs_unchanged=True,
)

@rules(forbid_names=["max", "min", "sorted"], forbid_methods=["sort"])

def task_rv01_best_player(players):
    ...
