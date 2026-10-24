from ego.testing import case

@case(
    args=([['аня', 10], ['борис', 5], ['вика', 7]], 'аня', 3),
    expected=[['аня', 13], ['борис', 5], ['вика', 7]],
    description='старый случай: имя есть',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([['аня', 10], ['борис', 5], ['вика', 7]], 'гоша', 4),
    expected=[['аня', 10], ['борис', 5], ['вика', 7], ['гоша', 4]],
    description='новое имя в конец',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([], 'аня', 5),
    expected=[['аня', 5]],
    description='пустая таблица',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([['аня', 10], ['борис', 5], ['вика', 7]], 'вика', -2),
    expected=[['аня', 10], ['борис', 5], ['вика', 5]],
    description='старый случай: очки уменьшаются',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([['аня', 10], ['борис', 5], ['вика', 7]], 'гоша', 0),
    expected=[['аня', 10], ['борис', 5], ['вика', 7], ['гоша', 0]],
    description='новый игрок с нулём очков',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([['аня', 1]], 'борис', 2),
    expected=[['аня', 1], ['борис', 2]],
    description='один старый, один новый',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([['аня', 1]], 'аня', 2),
    expected=[['аня', 3]],
    description='один игрок, имя есть',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

def task_fd19_add_score(scores, name, points):
    ...
