from ego.testing import case

@case(
    args=([100, 50], 10),
    expected=[90.0, 45.0],
    description='две цены',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([19.99, 5], 20),
    expected=[15.99, 4.0],
    description='округление до копеек',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([100], 0),
    expected=[100.0],
    description='скидки нет',
    level="smoke",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([], 10),
    expected=[],
    description='пустой список',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([100, 200], 100),
    expected=[0.0, 0.0],
    description='скидка сто процентов',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([9.99, 12], 15),
    expected=[8.49, 10.2],
    description='дробные результаты',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

@case(
    args=([0], 30),
    expected=[0.0],
    description='нулевая цена',
    level="full",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)

def task_li22_apply_discounts(prices, percent):
    ...
