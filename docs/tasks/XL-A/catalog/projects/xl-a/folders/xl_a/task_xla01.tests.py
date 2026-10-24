from ego.testing import case


HISTORY = [
    {"id": "a", "role": "user", "text": "Привет", "tokens": 2},
    {"id": "b", "role": "assistant", "text": "Привет!", "tokens": 3},
    {"id": "c", "role": "user", "text": "Где рейд?", "tokens": 4},
]


@case(
    args=(HISTORY, 7),
    expected=[
        {"id": "b", "role": "assistant", "text": "Привет!", "tokens": 3},
        {"id": "c", "role": "user", "text": "Где рейд?", "tokens": 4},
    ],
    description="Берётся последний непрерывный хвост, а не начало истории",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(HISTORY, 3),
    expected=[],
    description="Последнее сообщение не помещается: более старые не берём",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(HISTORY, 9),
    expected=[
        {"id": "a", "role": "user", "text": "Привет", "tokens": 2},
        {"id": "b", "role": "assistant", "text": "Привет!", "tokens": 3},
        {"id": "c", "role": "user", "text": "Где рейд?", "tokens": 4},
    ],
    description="Вся история ровно помещается в бюджет",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=([], 20),
    expected=[],
    description="Пустая история",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(HISTORY, 0),
    expected=[],
    description="Нулевой бюджет",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=([{"id": "one", "role": "user", "text": "Да", "tokens": 5}], 5),
    expected=[{"id": "one", "role": "user", "text": "Да", "tokens": 5}],
    description="Единственное сообщение ровно на весь бюджет",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=([{"id": "one", "role": "assistant", "text": "Ответ", "tokens": 5}], 4),
    expected=[],
    description="Единственное сообщение дороже бюджета",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "old", "role": "user", "text": "Старое", "tokens": 1},
            {"id": "large", "role": "assistant", "text": "Большое", "tokens": 8},
            {"id": "new", "role": "user", "text": "Новое", "tokens": 2},
        ],
        4,
    ),
    expected=[{"id": "new", "role": "user", "text": "Новое", "tokens": 2}],
    description="Нельзя перепрыгнуть через большое сообщение в середине",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(HISTORY, 8),
    expected=[
        {"id": "b", "role": "assistant", "text": "Привет!", "tokens": 3},
        {"id": "c", "role": "user", "text": "Где рейд?", "tokens": 4},
    ],
    description="Остаток бюджета не позволяет разделить старое сообщение",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {
                "id": "extra",
                "role": "user",
                "text": "",
                "tokens": 1,
                "channel": "party",
            }
        ],
        10,
    ),
    expected=[
        {
            "id": "extra",
            "role": "user",
            "text": "",
            "tokens": 1,
            "channel": "party",
        }
    ],
    description="Сохраняются все поля сообщения, в том числе дополнительные",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
def task_xla01_recent_history(messages, budget): ...
