from ego.testing import case

@case(
    args=([4, 8, 3, 2], 10),
    expected=[4, 3, 2],
    description='пропускаем то, что не влезло',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([5, 5, 5], 7),
    expected=[5],
    description='влезло только одно',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 2, 3], 100),
    expected=[1, 2, 3],
    description='влезло всё',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([], 5),
    expected=[],
    description='пустой список',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([9, 9], 5),
    expected=[],
    description='ничего не влезает',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([2, 6, 1], 7),
    expected=[6, 1],
    description='новые важнее старых',
    level="full",
    hide_expected=True,
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([6, 2, 7, 1, 3], 8),
    expected=[2, 1, 3],
    description='пропуски в середине',
    level="full",
    hide_expected=True,
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 2], 0),
    expected=[],
    description='нулевой бюджет',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([3, 3, 3, 3], 9),
    expected=[3, 3, 3],
    description='ровно по границе',
    level="full",
    hide_expected=True,
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

def task_rv02_pick_recent(costs, budget):
    ...
