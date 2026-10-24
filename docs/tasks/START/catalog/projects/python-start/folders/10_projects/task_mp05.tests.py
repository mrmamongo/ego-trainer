from ego.testing import case, rules

@case(
    args=(1, 100, 50),
    expected=1,
    description='угадали с первой',
    level="smoke",
)

@case(
    args=(1, 100, 25),
    expected=2,
    description='вторая попытка',
    level="smoke",
)

@case(
    args=(1, 10, 8),
    expected=2,
    description='маленький отрезок',
    level="smoke",
)

@case(
    args=(1, 100, 100),
    expected=7,
    description='верхняя граница',
    level="full",
)

@case(
    args=(1, 100, 1),
    expected=6,
    description='нижняя граница',
    level="full",
)

@case(
    args=(5, 5, 5),
    expected=1,
    description='отрезок из одного числа',
    level="full",
)

@case(
    args=(1, 1000, 1000),
    expected=10,
    description='до тысячи',
    level="full",
)

@case(
    args=(10, 20, 13),
    expected=3,
    description='отрезок не с единицы',
    level="full",
)

@case(
    args=(1, 100, 64),
    expected=7,
    description='степень двойки',
    level="full",
)

@case(
    args=(1, 10, 15),
    expected=-1,
    description='число выше отрезка',
    level="full",
)

@case(
    args=(1, 10, 0),
    expected=-1,
    description='число ниже отрезка',
    level="full",
)


@rules(
    forbid_names=["min", "max"],
    forbid_imports=["math"],
    allow_in=["game_report", "check_guess"],
    messages={
        "max": "max использовать нельзя: решай циклом",
        "min": "min использовать нельзя: решай циклом",
        "math": "Модуль math использовать нельзя: решай циклом",
    },
)

def task_mp05_best_strategy_steps(low, high, secret):
    ...
