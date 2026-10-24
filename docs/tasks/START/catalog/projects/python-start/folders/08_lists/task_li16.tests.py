from ego.testing import case, rules

@case(
    args=([3, 1, 3, 2, 1],),
    expected=[3, 1, 2],
    description='повторы вперемешку',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([5, 5, 5],),
    expected=[5],
    description='все одинаковые',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([1, 2, 3],),
    expected=[1, 2, 3],
    description='без повторов',
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
    args=([2, 1, 2, 1, 3, 3],),
    expected=[2, 1, 3],
    description='порядок первых появлений',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([-1, 0, -1, 0],),
    expected=[-1, 0],
    description='отрицательные и ноль',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([7],),
    expected=[7],
    description='один элемент',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)


@rules(
    forbid_names=["set", "dict"],
    messages={"set": "Множества и словари использовать нельзя: решай сборщиком и проверкой in"},
)

def task_li16_unique_in_order(nums):
    ...
