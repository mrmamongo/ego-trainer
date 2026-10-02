from ego.testing import case


@case(
    args=(
        {"events": [{"id": "e1", "title": "Raid", "capacity": 1, "members": ["m1"]}], "next_id": 2},
        {"tool": "join_event", "args": {"event_id": "e1", "member_id": "m2"}},
    ),
    expected={
        "status": "rejected",
        "state": {
            "events": [{"id": "e1", "title": "Raid", "capacity": 1, "members": ["m1"]}],
            "next_id": 2,
        },
        "result": None,
        "reason": "event_full",
    },
    description="Непустой словарь отказа не превращается в успех",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"events": [{"id": "e1", "title": "Raid", "capacity": 2, "members": []}], "next_id": 2},
        {"tool": "join_event", "args": {"event_id": "e1", "member_id": "m2"}},
    ),
    expected={
        "status": "done",
        "state": {
            "events": [{"id": "e1", "title": "Raid", "capacity": 2, "members": ["m2"]}],
            "next_id": 2,
        },
        "result": {"event_id": "e1", "member_id": "m2"},
        "reason": None,
    },
    description="Успешное вступление возвращает новое состояние и value обработчика",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"events": [], "next_id": 5},
        {"tool": "create_event", "args": {"title": "Raid", "capacity": 4}},
    ),
    expected={
        "status": "done",
        "state": {
            "events": [{"id": "e5", "title": "Raid", "capacity": 4, "members": []}],
            "next_id": 6,
        },
        "result": {"event_id": "e5"},
        "reason": None,
    },
    description="Создание использует текущий next_id и увеличивает его один раз",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"events": [{"id": "e1", "title": "Raid", "capacity": 1, "members": ["m1"]}], "next_id": 2},
        {"tool": "join_event", "args": {"event_id": "e1", "member_id": "m1"}},
    ),
    expected={
        "status": "rejected",
        "state": {
            "events": [{"id": "e1", "title": "Raid", "capacity": 1, "members": ["m1"]}],
            "next_id": 2,
        },
        "result": None,
        "reason": "already_joined",
    },
    description="Повторное вступление в полное событие возвращает already_joined",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"events": [{"id": "e1", "title": "Raid", "capacity": 1, "members": ["m1"]}], "next_id": 2},
        {"tool": "join_event", "args": {"event_id": "missing", "member_id": "m1"}},
    ),
    expected={
        "status": "rejected",
        "state": {
            "events": [{"id": "e1", "title": "Raid", "capacity": 1, "members": ["m1"]}],
            "next_id": 2,
        },
        "result": None,
        "reason": "unknown_event",
    },
    description="Неизвестное событие проверяется до остальных причин",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"events": [{"id": "e1", "title": "Raid", "capacity": 2, "members": []}], "next_id": 2},
        {"tool": "delete_event", "args": {}},
    ),
    expected={
        "status": "rejected",
        "state": {
            "events": [{"id": "e1", "title": "Raid", "capacity": 2, "members": []}],
            "next_id": 2,
        },
        "result": None,
        "reason": "unknown_tool",
    },
    description="Неизвестный инструмент не меняет состояние",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"events": [{"id": "e1", "title": "Raid", "capacity": 3, "members": ["m1"]}], "next_id": 2},
        {"tool": "join_event", "args": {"event_id": "e1", "member_id": "m1"}},
    ),
    expected={
        "status": "rejected",
        "state": {
            "events": [{"id": "e1", "title": "Raid", "capacity": 3, "members": ["m1"]}],
            "next_id": 2,
        },
        "result": None,
        "reason": "already_joined",
    },
    description="Повторное вступление запрещено и при свободных местах",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {
            "events": [
                {"id": "e1", "title": "Raid", "capacity": 2, "members": ["m1"]},
                {"id": "e2", "title": "Dungeon", "capacity": 3, "members": ["m3"]},
            ],
            "next_id": 3,
        },
        {"tool": "join_event", "args": {"event_id": "e2", "member_id": "m2"}},
    ),
    expected={
        "status": "done",
        "state": {
            "events": [
                {"id": "e1", "title": "Raid", "capacity": 2, "members": ["m1"]},
                {"id": "e2", "title": "Dungeon", "capacity": 3, "members": ["m3", "m2"]},
            ],
            "next_id": 3,
        },
        "result": {"event_id": "e2", "member_id": "m2"},
        "reason": None,
    },
    description="Добавляется участник только выбранного события с сохранением порядка",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"events": [{"id": "e7", "title": "Old", "capacity": 1, "members": ["m7"]}], "next_id": 43},
        {"tool": "create_event", "args": {"title": "Raid", "capacity": 4}},
    ),
    expected={
        "status": "done",
        "state": {
            "events": [
                {"id": "e7", "title": "Old", "capacity": 1, "members": ["m7"]},
                {"id": "e43", "title": "Raid", "capacity": 4, "members": []},
            ],
            "next_id": 44,
        },
        "result": {"event_id": "e43"},
        "reason": None,
    },
    description="Номер нового события не вычисляется по длине списка",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"events": [{"id": "e1", "title": "Raid", "capacity": 2, "members": ["m1"]}], "next_id": 2},
        {"tool": "join_event", "args": {"event_id": "e1", "member_id": "m2"}},
    ),
    expected={
        "status": "done",
        "state": {
            "events": [{"id": "e1", "title": "Raid", "capacity": 2, "members": ["m1", "m2"]}],
            "next_id": 2,
        },
        "result": {"event_id": "e1", "member_id": "m2"},
        "reason": None,
    },
    description="Последнее свободное место ещё допускает вступление",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
def task_xla14_dispatch(state, command): ...
