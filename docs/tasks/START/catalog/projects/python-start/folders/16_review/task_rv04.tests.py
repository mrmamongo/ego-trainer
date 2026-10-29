from ego.testing import case

@case(
    args=([5, 9, 1],),
    expected=[9, 5, 1],
    description='перемешанный список',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([3, 1, 2],),
    expected=[3, 2, 1],
    description='три числа',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([10, 40, 20, 30],),
    expected=[40, 30, 20, 10],
    description='четыре числа',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([],),
    expected=[],
    description='пустой список',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([7],),
    expected=[7],
    description='один элемент',
    level="full",
    hide_expected=True,
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([2, 2, 1],),
    expected=[2, 2, 1],
    description='повторы, уже по убыванию',
    level="full",
    hide_expected=True,
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 2, 3, 4, 5],),
    expected=[5, 4, 3, 2, 1],
    description='по возрастанию на входе',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

def task_rv04_leaderboard(scores):
    ...
