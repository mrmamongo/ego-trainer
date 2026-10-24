from ego.testing import case


QUEST = {
    "id": "q1",
    "objectives": [
        {"id": "wolves", "target": 3, "progress": 1},
        {"id": "herbs", "target": 5, "progress": 0},
    ],
}


@case(
    args=(
        QUEST,
        [
            {"objective_id": "wolves", "amount": 10},
            {"objective_id": "ghost", "amount": 1},
            {"objective_id": "herbs", "amount": 4},
        ],
    ),
    expected={
        "quest": {
            "id": "q1",
            "objectives": [
                {"id": "wolves", "target": 3, "progress": 3},
                {"id": "herbs", "target": 5, "progress": 4},
            ],
        },
        "completed": False,
        "rejected": [1],
    },
    description="События обновляют обе цели, превышение обрезается, чужая цель отклоняется",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"id": "q", "objectives": [{"id": "herbs", "target": 4, "progress": 1}]},
        [
            {"objective_id": "herbs", "amount": 1},
            {"objective_id": "herbs", "amount": 2},
            {"objective_id": "herbs", "amount": 10},
        ],
    ),
    expected={
        "quest": {
            "id": "q",
            "objectives": [
                {"id": "herbs", "target": 4, "progress": 4},
            ],
        },
        "completed": True,
        "rejected": [],
    },
    description="Одна цель сохраняет совместимость и накапливает повторные события",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"id": "empty", "objectives": []},
        [
            {"objective_id": "wolves", "amount": 2},
            {"objective_id": "herbs", "amount": 0},
        ],
    ),
    expected={"quest": {"id": "empty", "objectives": []}, "completed": True, "rejected": [0, 1]},
    description="Пустой набор целей завершён, все его события неизвестны",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(QUEST, []),
    expected={
        "quest": {
            "id": "q1",
            "objectives": [
                {"id": "wolves", "target": 3, "progress": 1},
                {"id": "herbs", "target": 5, "progress": 0},
            ],
        },
        "completed": False,
        "rejected": [],
    },
    description="Без событий квест остаётся прежним",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {
            "id": "q1",
            "objectives": [
                {"id": "wolves", "target": 3, "progress": 3},
                {"id": "herbs", "target": 5, "progress": 4},
            ],
        },
        [{"objective_id": "herbs", "amount": 1}],
    ),
    expected={
        "quest": {
            "id": "q1",
            "objectives": [
                {"id": "wolves", "target": 3, "progress": 3},
                {"id": "herbs", "target": 5, "progress": 5},
            ],
        },
        "completed": True,
        "rejected": [],
    },
    description="Следующий вызов завершает оставшуюся цель предыдущего состояния",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {
            "id": "done",
            "objectives": [
                {"id": "a", "target": 2, "progress": 2},
                {"id": "b", "target": 1, "progress": 1},
            ],
        },
        [
            {"objective_id": "b", "amount": 10},
            {"objective_id": "a", "amount": 0},
            {"objective_id": "unknown", "amount": 3},
        ],
    ),
    expected={
        "quest": {
            "id": "done",
            "objectives": [
                {"id": "a", "target": 2, "progress": 2},
                {"id": "b", "target": 1, "progress": 1},
            ],
        },
        "completed": True,
        "rejected": [2],
    },
    description="Завершённый квест не превышает target и продолжает отклонять неизвестные цели",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {
            "id": "partial",
            "objectives": [
                {"id": "first", "target": 1, "progress": 1},
                {"id": "second", "target": 2, "progress": 1},
            ],
        },
        [],
    ),
    expected={
        "quest": {
            "id": "partial",
            "objectives": [
                {"id": "first", "target": 1, "progress": 1},
                {"id": "second", "target": 2, "progress": 1},
            ],
        },
        "completed": False,
        "rejected": [],
    },
    description="Завершённая первая цель не означает завершение всего квеста",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {
            "id": "q",
            "objectives": [
                {"id": "a", "target": 3, "progress": 0},
                {"id": "b", "target": 3, "progress": 0},
            ],
        },
        [
            {"objective_id": "x", "amount": 0},
            {"objective_id": "b", "amount": 1},
            {"objective_id": "x", "amount": 2},
            {"objective_id": "a", "amount": 2},
            {"objective_id": "y", "amount": 3},
            {"objective_id": "b", "amount": 1},
        ],
    ),
    expected={
        "quest": {
            "id": "q",
            "objectives": [
                {"id": "a", "target": 3, "progress": 2},
                {"id": "b", "target": 3, "progress": 2},
            ],
        },
        "completed": False,
        "rejected": [0, 2, 4],
    },
    description="Индексы rejected относятся к исходному списку событий и не теряют повторы",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        QUEST,
        [
            {"objective_id": "herbs", "amount": 0},
            {"objective_id": "wolves", "amount": 0},
        ],
    ),
    expected={
        "quest": {
            "id": "q1",
            "objectives": [
                {"id": "wolves", "target": 3, "progress": 1},
                {"id": "herbs", "target": 5, "progress": 0},
            ],
        },
        "completed": False,
        "rejected": [],
    },
    description="Нулевые события известных целей принимаются без изменения прогресса",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {
            "id": "story",
            "title": "Помощь лесу",
            "metadata": {"zones": ["forest"]},
            "objectives": [
                {"id": "z", "target": 2, "progress": 0},
                {"id": "a", "target": 1, "progress": 0},
            ],
        },
        [{"objective_id": "a", "amount": 1}],
    ),
    expected={
        "quest": {
            "id": "story",
            "title": "Помощь лесу",
            "metadata": {"zones": ["forest"]},
            "objectives": [
                {"id": "z", "target": 2, "progress": 0},
                {"id": "a", "target": 1, "progress": 1},
            ],
        },
        "completed": False,
        "rejected": [],
    },
    description="Порядок целей и дополнительные вложенные поля квеста сохраняются",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=({"id": "empty", "objectives": []}, []),
    expected={"quest": {"id": "empty", "objectives": []}, "completed": True, "rejected": []},
    description="Пустой квест без событий завершён",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
def task_xla06_advance_quest(quest, events): ...
