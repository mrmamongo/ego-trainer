from ego.testing import case

@case(
    args=(["ok"], 3),
    expected=(1, "ok"),
    description='с первой попытки',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=(["timeout", "timeout", "ok"], 3),
    expected=(3, "ok"),
    description='две временные ошибки, потом успех',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=(["timeout", "forbidden", "ok"], 3),
    expected=(2, "forbidden"),
    description='постоянная ошибка останавливает повторы',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=(["timeout", "timeout", "timeout", "ok"], 3),
    expected=(3, "timeout"),
    description='попытки кончились раньше успеха',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=(["timeout", "ok"], 1),
    expected=(1, "timeout"),
    description='одна попытка — повторов нет',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=(["forbidden", "ok"], 2),
    expected=(1, "forbidden"),
    description='постоянная ошибка сразу',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=(["server_error"], 1),
    expected=(1, "server_error"),
    description='любая другая ошибка — тоже постоянная',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=(["timeout", "timeout", "timeout", "timeout", "ok"], 5),
    expected=(5, "ok"),
    description='успех на последней разрешённой попытке',
    level="full",
    check_inputs_unchanged=True,
    hide_expected=True,
)
def task_er16_retry(fn_results, max_attempts):
    ...
