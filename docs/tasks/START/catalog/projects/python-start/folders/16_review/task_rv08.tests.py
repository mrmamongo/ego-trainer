from ego.testing import case

@case(
    args=({'user': 'anna', 'item': 'potion', 'qty': 2, 'gold': 20}, {'sword': 50, 'potion': 5}),
    expected={'status': 'done', 'reason': None},
    description='всё в порядке',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({'user': 'anna', 'item': 'sword', 'qty': 2, 'gold': 20}, {'sword': 50, 'potion': 5}),
    expected={'status': 'rejected', 'reason': 'not_enough_gold'},
    description='не хватает золота',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({'user': '', 'item': 'potion', 'qty': 1, 'gold': 99}, {'sword': 50, 'potion': 5}),
    expected={'status': 'rejected', 'reason': 'no_user'},
    description='пустое имя',
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({'item': 'potion', 'qty': 1, 'gold': 99}, {'sword': 50, 'potion': 5}),
    expected={'status': 'rejected', 'reason': 'no_user'},
    description='нет ключа user',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({'user': 'anna', 'item': 'shield', 'qty': 1, 'gold': 99}, {'sword': 50, 'potion': 5}),
    expected={'status': 'rejected', 'reason': 'unknown_item'},
    description='неизвестный товар',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({'user': '', 'item': 'shield', 'qty': 0, 'gold': 0}, {'sword': 50, 'potion': 5}),
    expected={'status': 'rejected', 'reason': 'no_user'},
    description='несколько причин: побеждает первая',
    level="full",
    hide_expected=True,
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({'user': 'anna', 'item': 'shield', 'qty': 0, 'gold': 0}, {'sword': 50, 'potion': 5}),
    expected={'status': 'rejected', 'reason': 'unknown_item'},
    description='товар раньше количества',
    level="full",
    hide_expected=True,
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({'user': 'anna', 'item': 'sword', 'qty': 0, 'gold': 0}, {'sword': 50, 'potion': 5}),
    expected={'status': 'rejected', 'reason': 'bad_qty'},
    description='количество раньше золота',
    level="full",
    hide_expected=True,
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({'user': 'anna', 'item': 'potion', 'qty': 11, 'gold': 1000}, {'sword': 50, 'potion': 5}),
    expected={'status': 'rejected', 'reason': 'bad_qty'},
    description='слишком много',
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)

@case(
    args=({'user': 'anna', 'item': 'potion', 'qty': 10, 'gold': 50}, {'sword': 50, 'potion': 5}),
    expected={'status': 'done', 'reason': None},
    description='границы: 10 штук и золота ровно хватает',
    level="full",
    hide_expected=True,
    comparison="value",
    check_inputs_unchanged=True,
)

def task_rv08_validate_request(request, prices):
    ...
