from ego.testing import case


@case(
    args=(
        {
            "A": {"preferences": {"language": "ru"}, "theme": "dark"},
            "B": {"preferences": {"language": "ru"}, "theme": "light"},
        },
        "A",
        "en",
    ),
    expected={
        "A": {"preferences": {"language": "en"}, "theme": "dark"},
        "B": {"preferences": {"language": "ru"}, "theme": "light"},
    },
    description="Смена языка A сохраняет независимый B и исходный A",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {
            "A": {"preferences": {"language": "ru"}, "theme": "dark"},
            "B": {"preferences": {"language": "ru"}, "theme": "light"},
        },
        "A",
        "en",
    ),
    expected={
        "A": {"preferences": {"language": "en"}, "theme": "dark"},
        "B": {"preferences": {"language": "ru"}, "theme": "light"},
    },
    description="Общая ссылка A.preferences и B.preferences разрывается перед изменением",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
    input_aliases=(((0, "B", "preferences"), (0, "A", "preferences")),),
)
@case(
    args=(
        {
            "A": {"preferences": {"language": "ru"}, "theme": "dark"},
            "B": {"preferences": {"language": "ru"}, "theme": "light"},
        },
        "missing",
        "en",
    ),
    expected={
        "A": {"preferences": {"language": "ru"}, "theme": "dark"},
        "B": {"preferences": {"language": "ru"}, "theme": "light"},
    },
    description="Неизвестный пользователь не добавляется, результат глубоко изолирован",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({}, "missing", "en"),
    expected={},
    description="Пустой список профилей возвращается пустым",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {
            "A": {"preferences": {"language": "ru"}, "theme": "dark"},
            "B": {"preferences": {"language": "ru"}, "theme": "light"},
        },
        "A",
        "ru",
    ),
    expected={
        "A": {"preferences": {"language": "ru"}, "theme": "dark"},
        "B": {"preferences": {"language": "ru"}, "theme": "light"},
    },
    description="Повтор прежнего языка всё равно возвращает независимый снимок",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {
            "A": {"preferences": {"language": "ru"}, "theme": "dark"},
            "B": {"preferences": {"language": "ru"}, "theme": "light"},
        },
        "B",
        "de",
    ),
    expected={
        "A": {"preferences": {"language": "ru"}, "theme": "dark"},
        "B": {"preferences": {"language": "de"}, "theme": "light"},
    },
    description="Выбор второго пользователя не меняет первого",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {
            "A": {
                "preferences": {"language": "ru", "notifications": {"dm": True}, "volume": 0},
                "history": {"last": None},
                "empty": {},
            },
            "B": {"preferences": {"language": "en"}, "rank": 1},
        },
        "A",
        "fr",
    ),
    expected={
        "A": {
            "preferences": {"language": "fr", "notifications": {"dm": True}, "volume": 0},
            "history": {"last": None},
            "empty": {},
        },
        "B": {"preferences": {"language": "en"}, "rank": 1},
    },
    description="Соседние вложенные поля, пустые словари и ложные значения сохраняются",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {
            "A": {"preferences": {"language": "ru"}, "theme": "dark"},
            "B": {"preferences": {"language": "ru"}, "theme": "dark"},
        },
        "A",
        "en",
    ),
    expected={
        "A": {"preferences": {"language": "en"}, "theme": "dark"},
        "B": {"preferences": {"language": "ru"}, "theme": "dark"},
    },
    description="Два пользователя могут ссылаться на один и тот же целый профиль",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
    input_aliases=(((0, "B"), (0, "A")),),
)
@case(
    args=({"A": {"preferences": {"language": "ru"}, "backup": {"language": "ru"}}}, "A", "en"),
    expected={"A": {"preferences": {"language": "en"}, "backup": {"language": "ru"}}},
    description="Общая ссылка preferences и другого поля не меняет значение другого поля",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
    input_aliases=(((0, "A", "backup"), (0, "A", "preferences")),),
)
@case(
    args=(
        {
            "A": {"preferences": {"language": "ru"}, "theme": "dark"},
            "B": {"preferences": {"language": "ru"}, "theme": "light"},
        },
        "A",
        "",
    ),
    expected={
        "A": {"preferences": {"language": ""}, "theme": "dark"},
        "B": {"preferences": {"language": "ru"}, "theme": "light"},
    },
    description="Строка языка передаётся без добавленной валидации или нормализации",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
def task_xla23_set_user_language(profiles, user_id, language): ...
