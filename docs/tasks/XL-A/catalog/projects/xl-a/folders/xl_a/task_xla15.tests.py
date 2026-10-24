from ego.testing import case


@case(
    args=(
        {"events": [], "next_id": 1},
        {"tool": "create_event", "args": {"title": "Raid", "capacity": 4}},
        "preview",
    ),
    expected={
        "status": "preview",
        "state": {"events": [], "next_id": 1},
        "result": {"event_id": "e1"},
        "reason": None,
        "preview_state": {
            "events": [{"id": "e1", "title": "Raid", "capacity": 4, "members": []}],
            "next_id": 2,
        },
    },
    description="Предпросмотр создания показывает будущее и сохраняет реальный next_id",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"events": [], "next_id": 1},
        {"tool": "create_event", "args": {"title": "Raid", "capacity": 4}},
    ),
    expected={
        "status": "done",
        "state": {
            "events": [{"id": "e1", "title": "Raid", "capacity": 4, "members": []}],
            "next_id": 2,
        },
        "result": {"event_id": "e1"},
        "reason": None,
        "preview_state": None,
    },
    description="Режим по умолчанию сохраняет применение команды",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"events": [], "next_id": 1},
        {"tool": "join_event", "args": {"event_id": "missing", "member_id": "m1"}},
        "preview",
    ),
    expected={
        "status": "rejected",
        "state": {"events": [], "next_id": 1},
        "result": None,
        "reason": "unknown_event",
        "preview_state": None,
    },
    description="Отказ предпросмотра не создаёт прогноз состояния",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"events": [{"id": "e1", "title": "Raid", "capacity": 2, "members": []}], "next_id": 2},
        {"tool": "join_event", "args": {"event_id": "e1", "member_id": "m2"}},
        "preview",
    ),
    expected={
        "status": "preview",
        "state": {
            "events": [{"id": "e1", "title": "Raid", "capacity": 2, "members": []}],
            "next_id": 2,
        },
        "result": {"event_id": "e1", "member_id": "m2"},
        "reason": None,
        "preview_state": {
            "events": [{"id": "e1", "title": "Raid", "capacity": 2, "members": ["m2"]}],
            "next_id": 2,
        },
    },
    description="Предпросмотр вступления сохраняет исходный список участников",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"events": [{"id": "e1", "title": "Raid", "capacity": 2, "members": []}], "next_id": 2},
        {"tool": "join_event", "args": {"event_id": "e1", "member_id": "m2"}},
        "apply",
    ),
    expected={
        "status": "done",
        "state": {
            "events": [{"id": "e1", "title": "Raid", "capacity": 2, "members": ["m2"]}],
            "next_id": 2,
        },
        "result": {"event_id": "e1", "member_id": "m2"},
        "reason": None,
        "preview_state": None,
    },
    description="Явный apply применяет вступление и не возвращает preview_state",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"events": [{"id": "e1", "title": "Raid", "capacity": 1, "members": ["m1"]}], "next_id": 2},
        {"tool": "join_event", "args": {"event_id": "e1", "member_id": "m2"}},
        "apply",
    ),
    expected={
        "status": "rejected",
        "state": {
            "events": [{"id": "e1", "title": "Raid", "capacity": 1, "members": ["m1"]}],
            "next_id": 2,
        },
        "result": None,
        "reason": "event_full",
        "preview_state": None,
    },
    description="Штатный отказ в apply сохраняет прежний контракт",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"events": [{"id": "e1", "title": "Raid", "capacity": 1, "members": ["m1"]}], "next_id": 2},
        {"tool": "join_event", "args": {"event_id": "e1", "member_id": "m2"}},
        "preview",
    ),
    expected={
        "status": "rejected",
        "state": {
            "events": [{"id": "e1", "title": "Raid", "capacity": 1, "members": ["m1"]}],
            "next_id": 2,
        },
        "result": None,
        "reason": "event_full",
        "preview_state": None,
    },
    description="Полное событие отклоняется и в preview",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"events": [{"id": "e1", "title": "Raid", "capacity": 1, "members": ["m1"]}], "next_id": 2},
        {"tool": "join_event", "args": {"event_id": "e1", "member_id": "m1"}},
        "preview",
    ),
    expected={
        "status": "rejected",
        "state": {
            "events": [{"id": "e1", "title": "Raid", "capacity": 1, "members": ["m1"]}],
            "next_id": 2,
        },
        "result": None,
        "reason": "already_joined",
        "preview_state": None,
    },
    description="Preview сохраняет приоритет already_joined перед event_full",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"events": [{"id": "e1", "title": "Raid", "capacity": 2, "members": []}], "next_id": 2},
        {"tool": "delete_event", "args": {}},
        "preview",
    ),
    expected={
        "status": "rejected",
        "state": {
            "events": [{"id": "e1", "title": "Raid", "capacity": 2, "members": []}],
            "next_id": 2,
        },
        "result": None,
        "reason": "unknown_tool",
        "preview_state": None,
    },
    description="Неизвестная команда не получает предпросмотр",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"events": [{"id": "e2", "title": "Old", "capacity": 1, "members": ["m2"]}], "next_id": 9},
        {"tool": "create_event", "args": {"title": "Raid", "capacity": 4}},
        "preview",
    ),
    expected={
        "status": "preview",
        "state": {
            "events": [{"id": "e2", "title": "Old", "capacity": 1, "members": ["m2"]}],
            "next_id": 9,
        },
        "result": {"event_id": "e9"},
        "reason": None,
        "preview_state": {
            "events": [
                {"id": "e2", "title": "Old", "capacity": 1, "members": ["m2"]},
                {"id": "e9", "title": "Raid", "capacity": 4, "members": []},
            ],
            "next_id": 10,
        },
    },
    description="Прогноз создания сохраняет существующие события и независимый будущий счётчик",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
def task_xla15_preview_action(state, command, mode="apply"): ...
