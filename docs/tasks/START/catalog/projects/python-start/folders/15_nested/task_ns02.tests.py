from ego.testing import case, rules

@case(
    args=([1, 2, 3],),
    expected=6,
    description='простой список',
    level="smoke",
)

@case(
    args=([],),
    expected=0,
    description='пустой список: нужна база',
    level="smoke",
)

@case(
    args=([7],),
    expected=7,
    description='один элемент',
    level="smoke",
)

@case(
    args=([-5, 5, -1],),
    expected=-1,
    description='отрицательные числа',
    level="full",
)

@case(
    args=([0, 0],),
    expected=0,
    description='нули',
    level="full",
)

@case(
    args=(list(range(1, 101)),),
    expected=5050,
    description='длинный список',
    level="full",
)


@rules(
    forbid_names=["sum"],
    forbid_nodes=["For", "While"],
    messages={
        "sum": "Встроенную sum использовать нельзя: сумму собирает рекурсия",
        "For": "Циклы здесь не нужны: используй рекурсивный вызов",
        "While": "Циклы здесь не нужны: используй рекурсивный вызов",
    },
)

def task_ns02_sum_list(numbers):
    ...
