from ego.testing import case, rules

@case(
    args=(["add 5", "sub x", "add 3"],),
    expected=[5, "bad_number", 8],
    description='плохая строка в середине не останавливает остальные',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=(["add 10", "sub 4", "sub 6"],),
    expected=[10, 6, 0],
    description='только правильные команды',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=(["mul 2", "sub 1"],),
    expected=["unknown_command", "not_enough"],
    description='неизвестная команда и нехватка',
    level="smoke",
    check_inputs_unchanged=True,
)

@case(
    args=([],),
    expected=[],
    description='пустой список команд',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=(["", "   ", "ADD 5"],),
    expected=["unknown_command", "unknown_command", "unknown_command"],
    description='пустая строка, пробелы, другой регистр',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=(["add", "add 5 6", "add 4.5", "add -3", "sub"],),
    expected=["bad_number", "bad_number", "bad_number", "bad_number", "bad_number"],
    description='разные виды плохого числа',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=(["add 5", "sub 9", "add 1", "sub 6", "sub 1"],),
    expected=[5, "not_enough", 6, 0, "not_enough"],
    description='ошибка not_enough не меняет total',
    level="full",
    check_inputs_unchanged=True,
)

@case(
    args=(["add 0", "sub 0", "add x", "add 7"],),
    expected=[0, 0, "bad_number", 7],
    description='ноль — допустимое число',
    level="full",
    check_inputs_unchanged=True,
    hide_expected=True,
)


@rules(
    forbid_methods=["isdigit"],
    messages={"isdigit": "здесь число проверяй через try/except ValueError"},
)

def task_er11_process_lines(lines):
    ...
