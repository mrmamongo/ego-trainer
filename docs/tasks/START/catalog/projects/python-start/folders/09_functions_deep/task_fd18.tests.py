from ego.testing import case

@case(
    args=([['аня', 10], ['борис', 5], ['вика', 7]], 'аня', 3),
    expected=[['аня', 13], ['борис', 5], ['вика', 7]],
    description='очки первому игроку',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([['аня', 10], ['борис', 5], ['вика', 7]], 'борис', 0),
    expected=[['аня', 10], ['борис', 5], ['вика', 7]],
    description='ноль очков, таблица та же по значениям',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([['аня', 10], ['борис', 5], ['вика', 7]], 'вика', -2),
    expected=[['аня', 10], ['борис', 5], ['вика', 5]],
    description='очки уменьшаются',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([['аня', 10], ['борис', 5], ['вика', 7]], 'борис', -10),
    expected=[['аня', 10], ['борис', -5], ['вика', 7]],
    description='итог становится отрицательным',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([['аня', 1]], 'аня', 1),
    expected=[['аня', 2]],
    description='один игрок',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([['аня', 0], ['борис', 0]], 'борис', 4),
    expected=[['аня', 0], ['борис', 4]],
    description='последний игрок',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

def task_fd18_add_score(scores, name, points):
    ...
