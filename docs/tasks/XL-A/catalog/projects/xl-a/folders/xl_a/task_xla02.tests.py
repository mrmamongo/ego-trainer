from ego.testing import case


HISTORY = [
    {"id": "s", "role": "system", "text": "Кратко", "tokens": 3},
    {"id": "u1", "role": "user", "text": "Привет", "tokens": 4},
    {"id": "a1", "role": "assistant", "text": "Привет!", "tokens": 4},
    {"id": "u2", "role": "user", "text": "Где рейд?", "tokens": 5},
]


@case(
    args=(HISTORY, 8),
    expected={
        "status": "ready",
        "messages": [
            {"id": "s", "role": "system", "text": "Кратко", "tokens": 3},
            {"id": "u2", "role": "user", "text": "Где рейд?", "tokens": 5},
        ],
        "used_tokens": 8,
        "missing_tokens": 0,
    },
    description="Инструкция и последний вопрос закреплены при точном бюджете",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(HISTORY, 7),
    expected={"status": "too_large", "messages": [], "used_tokens": 0, "missing_tokens": 1},
    description="Отказ, когда обязательным сообщениям не хватает одного токена",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(HISTORY, 16),
    expected={
        "status": "ready",
        "messages": [
            {"id": "s", "role": "system", "text": "Кратко", "tokens": 3},
            {"id": "u1", "role": "user", "text": "Привет", "tokens": 4},
            {"id": "a1", "role": "assistant", "text": "Привет!", "tokens": 4},
            {"id": "u2", "role": "user", "text": "Где рейд?", "tokens": 5},
        ],
        "used_tokens": 16,
        "missing_tokens": 0,
    },
    description="Полностью помещающаяся история сохраняет прежнее поведение",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(HISTORY, 12),
    expected={
        "status": "ready",
        "messages": [
            {"id": "s", "role": "system", "text": "Кратко", "tokens": 3},
            {"id": "a1", "role": "assistant", "text": "Привет!", "tokens": 4},
            {"id": "u2", "role": "user", "text": "Где рейд?", "tokens": 5},
        ],
        "used_tokens": 12,
        "missing_tokens": 0,
    },
    description="Среди необязательных приоритет имеет более новое сообщение",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "s", "role": "system", "text": "Правило", "tokens": 1},
            {"id": "old", "role": "user", "text": "Раньше", "tokens": 2},
            {"id": "large", "role": "assistant", "text": "Длинный ответ", "tokens": 9},
            {"id": "u", "role": "user", "text": "Сейчас", "tokens": 2},
            {"id": "a", "role": "assistant", "text": "Да", "tokens": 1},
        ],
        6,
    ),
    expected={
        "status": "ready",
        "messages": [
            {"id": "s", "role": "system", "text": "Правило", "tokens": 1},
            {"id": "old", "role": "user", "text": "Раньше", "tokens": 2},
            {"id": "u", "role": "user", "text": "Сейчас", "tokens": 2},
            {"id": "a", "role": "assistant", "text": "Да", "tokens": 1},
        ],
        "used_tokens": 6,
        "missing_tokens": 0,
    },
    description="Большое необязательное сообщение пропускается, поиск продолжается",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=([], 0),
    expected={"status": "ready", "messages": [], "used_tokens": 0, "missing_tokens": 0},
    description="Пустая история успешна даже при нулевом бюджете",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "old", "role": "assistant", "text": "Старое", "tokens": 4},
            {"id": "new", "role": "assistant", "text": "Новое", "tokens": 2},
        ],
        3,
    ),
    expected={
        "status": "ready",
        "messages": [
            {"id": "new", "role": "assistant", "text": "Новое", "tokens": 2},
        ],
        "used_tokens": 2,
        "missing_tokens": 0,
    },
    description="История без system и user заполняется необязательными сообщениями",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "s", "role": "system", "text": "Правило", "tokens": 3},
            {"id": "large", "role": "assistant", "text": "Длинно", "tokens": 10},
            {"id": "a", "role": "assistant", "text": "Коротко", "tokens": 2},
        ],
        5,
    ),
    expected={
        "status": "ready",
        "messages": [
            {"id": "s", "role": "system", "text": "Правило", "tokens": 3},
            {"id": "a", "role": "assistant", "text": "Коротко", "tokens": 2},
        ],
        "used_tokens": 5,
        "missing_tokens": 0,
    },
    description="Без пользователя закрепляется только system",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "u", "role": "user", "text": "Вопрос", "tokens": 4},
            {"id": "large", "role": "assistant", "text": "Длинно", "tokens": 9},
            {"id": "a", "role": "assistant", "text": "Коротко", "tokens": 1},
        ],
        5,
    ),
    expected={
        "status": "ready",
        "messages": [
            {"id": "u", "role": "user", "text": "Вопрос", "tokens": 4},
            {"id": "a", "role": "assistant", "text": "Коротко", "tokens": 1},
        ],
        "used_tokens": 5,
        "missing_tokens": 0,
    },
    description="Без system последний user закреплён, даже если после него есть ответы",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(HISTORY, 0),
    expected={"status": "too_large", "messages": [], "used_tokens": 0, "missing_tokens": 8},
    description="Недостающие токены считаются только для обязательной части",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "old", "role": "assistant", "text": "Коротко", "tokens": 2},
            {"id": "new", "role": "assistant", "text": "Длинно", "tokens": 9},
        ],
        2,
    ),
    expected={
        "status": "ready",
        "messages": [
            {"id": "old", "role": "assistant", "text": "Коротко", "tokens": 2},
        ],
        "used_tokens": 2,
        "missing_tokens": 0,
    },
    description="Без обязательных сообщений слишком большой конец можно пропустить",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
def task_xla02_pinned_context(messages, budget): ...
