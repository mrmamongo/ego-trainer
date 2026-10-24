from ego.testing import case


SYSTEM = {"id": "s", "role": "system", "text": "Кратко", "tokens": 3}
HISTORY = [{"id": "h", "role": "assistant", "text": "Привет", "tokens": 4}]
USER = {"id": "u", "role": "user", "text": "Где рейд?", "tokens": 5}


@case(
    args=(SYSTEM, HISTORY, USER, 8),
    expected={
        "status": "ready",
        "messages": [
            {"role": "system", "content": "Кратко"},
            {"role": "user", "content": "Где рейд?"},
        ],
        "used_tokens": 8,
        "missing_tokens": 0,
        "dropped_ids": ["h"],
    },
    description="Запрос включает закреплённые сообщения в формате API",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(SYSTEM, HISTORY, USER, 7),
    expected={
        "status": "too_large",
        "messages": [],
        "used_tokens": 0,
        "missing_tokens": 1,
        "dropped_ids": ["s", "h", "u"],
    },
    description="При отказе dropped_ids содержит и system, и новый вопрос",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(SYSTEM, [], USER, 8),
    expected={
        "status": "ready",
        "messages": [
            {"role": "system", "content": "Кратко"},
            {"role": "user", "content": "Где рейд?"},
        ],
        "used_tokens": 8,
        "missing_tokens": 0,
        "dropped_ids": [],
    },
    description="Пустая история и бюджет ровно на обязательные сообщения",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(SYSTEM, HISTORY, USER, 12),
    expected={
        "status": "ready",
        "messages": [
            {"role": "system", "content": "Кратко"},
            {"role": "assistant", "content": "Привет"},
            {"role": "user", "content": "Где рейд?"},
        ],
        "used_tokens": 12,
        "missing_tokens": 0,
        "dropped_ids": [],
    },
    description="Вся последовательность включается один раз и в исходном порядке",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(SYSTEM, HISTORY, USER, 0),
    expected={
        "status": "too_large",
        "messages": [],
        "used_tokens": 0,
        "missing_tokens": 8,
        "dropped_ids": ["s", "h", "u"],
    },
    description="Нулевой бюджет передаёт точный дефицит обязательных сообщений",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        SYSTEM,
        [
            {"id": "z", "role": "user", "text": "Первый", "tokens": 2},
            {"id": "a", "role": "assistant", "text": "Второй", "tokens": 2},
        ],
        USER,
        8,
    ),
    expected={
        "status": "ready",
        "messages": [
            {"role": "system", "content": "Кратко"},
            {"role": "user", "content": "Где рейд?"},
        ],
        "used_tokens": 8,
        "missing_tokens": 0,
        "dropped_ids": ["z", "a"],
    },
    description="Исключённые ID сохраняют хронологический, а не алфавитный порядок",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"id": "s", "role": "system", "text": "Правило", "tokens": 1},
        [
            {"id": "old", "role": "user", "text": "Раньше", "tokens": 2},
            {"id": "large", "role": "assistant", "text": "Длинно", "tokens": 9},
            {"id": "new", "role": "assistant", "text": "Да", "tokens": 1},
        ],
        {"id": "u", "role": "user", "text": "Сейчас", "tokens": 2},
        6,
    ),
    expected={
        "status": "ready",
        "messages": [
            {"role": "system", "content": "Правило"},
            {"role": "user", "content": "Раньше"},
            {"role": "assistant", "content": "Да"},
            {"role": "user", "content": "Сейчас"},
        ],
        "used_tokens": 6,
        "missing_tokens": 0,
        "dropped_ids": ["large"],
    },
    description="Сборка использует пропуск слишком большого необязательного сообщения",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"id": "s", "role": "system", "text": "Правило", "tokens": 1},
        [
            {"id": "old", "role": "user", "text": "Старое", "tokens": 2},
            {"id": "middle", "role": "assistant", "text": "Среднее", "tokens": 2},
            {"id": "new", "role": "assistant", "text": "Новое", "tokens": 2},
        ],
        {"id": "u", "role": "user", "text": "Вопрос", "tokens": 1},
        5,
    ),
    expected={
        "status": "ready",
        "messages": [
            {"role": "system", "content": "Правило"},
            {"role": "assistant", "content": "Новое"},
            {"role": "user", "content": "Вопрос"},
        ],
        "used_tokens": 4,
        "missing_tokens": 0,
        "dropped_ids": ["old", "middle"],
    },
    description="Более новая история имеет приоритет, неиспользованный токен допустим",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"id": "sys", "role": "system", "text": "Строка 1\nСтрока 2", "tokens": 1},
        [{"id": "extra", "role": "assistant", "text": "", "tokens": 1, "source": "ui"}],
        {"id": "ask", "role": "user", "text": "Привет, мир!", "tokens": 1},
        9,
    ),
    expected={
        "status": "ready",
        "messages": [
            {"role": "system", "content": "Строка 1\nСтрока 2"},
            {"role": "assistant", "content": ""},
            {"role": "user", "content": "Привет, мир!"},
        ],
        "used_tokens": 3,
        "missing_tokens": 0,
        "dropped_ids": [],
    },
    description="API сохраняет текст, но исключает внутренние ID, tokens и прочие поля",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"id": "z-system", "role": "system", "text": "Правило", "tokens": 4},
        [],
        {"id": "a-user", "role": "user", "text": "Вопрос", "tokens": 1},
        4,
    ),
    expected={
        "status": "too_large",
        "messages": [],
        "used_tokens": 0,
        "missing_tokens": 1,
        "dropped_ids": ["z-system", "a-user"],
    },
    description="Отказ с пустой историей сохраняет порядок всех обязательных ID",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
def task_xla03_build_request(system_message, history, user_message, budget): ...
