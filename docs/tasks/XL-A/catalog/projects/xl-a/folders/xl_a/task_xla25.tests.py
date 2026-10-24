from ego.testing import case


@case(
    args=(
        {"events": {}, "announcements": [], "next_id": 4},
        {"tool": "create_event", "args": {"title": " Raid ", "capacity": 2}},
    ),
    expected={
        "status": "done",
        "state": {
            "events": {"e4": {"title": "Raid", "capacity": 2, "members": []}},
            "announcements": [],
            "next_id": 5,
        },
        "result": {"event_id": "e4"},
        "reason": None,
    },
    description="Создание обрезает заголовок и расходует ровно один ID",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {
            "events": {"e4": {"title": "Raid", "capacity": 2, "members": ["X"]}},
            "announcements": [{"event_id": "e4", "text": "Before"}],
            "next_id": 5,
        },
        {"tool": "join_event", "args": {"event_id": "e4", "member_id": " Sam "}},
    ),
    expected={
        "status": "done",
        "state": {
            "events": {"e4": {"title": "Raid", "capacity": 2, "members": ["X", " Sam "]}},
            "announcements": [{"event_id": "e4", "text": "Before"}],
            "next_id": 5,
        },
        "result": {"event_id": "e4", "member_id": " Sam "},
        "reason": None,
    },
    description="Участник добавляется в конец, его идентификатор не обрезается",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {
            "events": {"e4": {"title": "Raid", "capacity": 2, "members": ["X"]}},
            "announcements": [{"event_id": "e4", "text": "Before"}],
            "next_id": 5,
        },
        {"tool": "prepare_announcement", "args": {"event_id": "e4", "text": "  Meet\n"}},
    ),
    expected={
        "status": "done",
        "state": {
            "events": {"e4": {"title": "Raid", "capacity": 2, "members": ["X"]}},
            "announcements": [
                {"event_id": "e4", "text": "Before"},
                {"event_id": "e4", "text": "Meet"},
            ],
            "next_id": 5,
        },
        "result": {"announcement_index": 1},
        "reason": None,
    },
    description="Объявление обрезает текст и возвращает индекс после существующей записи",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {
            "events": {"e1": {"title": "Raid", "capacity": 1, "members": ["Sam"]}},
            "announcements": [],
            "next_id": 2,
        },
        {"tool": "unknown", "args": {"title": None, "capacity": False, "event_id": "missing"}},
    ),
    expected={
        "status": "rejected",
        "state": {
            "events": {"e1": {"title": "Raid", "capacity": 1, "members": ["Sam"]}},
            "announcements": [],
            "next_id": 2,
        },
        "result": None,
        "reason": "unknown_tool",
    },
    description="Неизвестная команда проверяется раньше аргументов",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"events": {}, "announcements": [], "next_id": 4},
        {"tool": "create_event", "args": {"title": " \t", "capacity": 0}},
    ),
    expected={
        "status": "rejected",
        "state": {"events": {}, "announcements": [], "next_id": 4},
        "result": None,
        "reason": "invalid_title",
    },
    description="Пустой после strip заголовок проверяется раньше вместимости",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"events": {}, "announcements": [], "next_id": 4},
        {"tool": "create_event", "args": {"title": "Raid", "capacity": True}},
    ),
    expected={
        "status": "rejected",
        "state": {"events": {}, "announcements": [], "next_id": 4},
        "result": None,
        "reason": "invalid_capacity",
    },
    description="Булева вместимость не считается целым числом",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {
            "events": {"e1": {"title": "Raid", "capacity": 1, "members": ["Sam"]}},
            "announcements": [],
            "next_id": 2,
        },
        {"tool": "join_event", "args": {"event_id": " e1 ", "member_id": None}},
    ),
    expected={
        "status": "rejected",
        "state": {
            "events": {"e1": {"title": "Raid", "capacity": 1, "members": ["Sam"]}},
            "announcements": [],
            "next_id": 2,
        },
        "result": None,
        "reason": "unknown_event",
    },
    description="ID события не обрезается; неизвестное событие проверяется раньше участника",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {
            "events": {"e1": {"title": "Raid", "capacity": 1, "members": ["Sam"]}},
            "announcements": [],
            "next_id": 2,
        },
        {"tool": "join_event", "args": {"event_id": "e1", "member_id": ""}},
    ),
    expected={
        "status": "rejected",
        "state": {
            "events": {"e1": {"title": "Raid", "capacity": 1, "members": ["Sam"]}},
            "announcements": [],
            "next_id": 2,
        },
        "result": None,
        "reason": "invalid_member",
    },
    description="Пустой участник проверяется раньше заполненности события",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {
            "events": {"e1": {"title": "Raid", "capacity": 1, "members": ["Sam"]}},
            "announcements": [],
            "next_id": 2,
        },
        {"tool": "join_event", "args": {"event_id": "e1", "member_id": "Sam"}},
    ),
    expected={
        "status": "rejected",
        "state": {
            "events": {"e1": {"title": "Raid", "capacity": 1, "members": ["Sam"]}},
            "announcements": [],
            "next_id": 2,
        },
        "result": None,
        "reason": "already_joined",
    },
    description="Повторное участие проверяется раньше заполненности",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {
            "events": {"e1": {"title": "Raid", "capacity": 1, "members": ["Sam"]}},
            "announcements": [],
            "next_id": 2,
        },
        {"tool": "join_event", "args": {"event_id": "e1", "member_id": "B"}},
    ),
    expected={
        "status": "rejected",
        "state": {
            "events": {"e1": {"title": "Raid", "capacity": 1, "members": ["Sam"]}},
            "announcements": [],
            "next_id": 2,
        },
        "result": None,
        "reason": "event_full",
    },
    description="Новый участник не помещается в заполненное событие",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {
            "events": {"e1": {"title": "Raid", "capacity": 1, "members": ["Sam"]}},
            "announcements": [],
            "next_id": 2,
        },
        {"tool": "prepare_announcement", "args": {"event_id": "missing", "text": ""}},
    ),
    expected={
        "status": "rejected",
        "state": {
            "events": {"e1": {"title": "Raid", "capacity": 1, "members": ["Sam"]}},
            "announcements": [],
            "next_id": 2,
        },
        "result": None,
        "reason": "unknown_event",
    },
    description="Для объявления неизвестное событие проверяется раньше текста",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {
            "events": {"e1": {"title": "Raid", "capacity": 1, "members": ["Sam"]}},
            "announcements": [],
            "next_id": 2,
        },
        {"tool": "prepare_announcement", "args": {"event_id": "e1", "text": " \n\t"}},
    ),
    expected={
        "status": "rejected",
        "state": {
            "events": {"e1": {"title": "Raid", "capacity": 1, "members": ["Sam"]}},
            "announcements": [],
            "next_id": 2,
        },
        "result": None,
        "reason": "invalid_text",
    },
    description="Пустое объявление не добавляется и возвращает result=None",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
def task_xla25_run_action(state, command): ...
