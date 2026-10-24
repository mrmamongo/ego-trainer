from ego.testing import case


@case(
    args=(
        {"tool": "create_event", "args": {"title": "  Raid \n", "capacity": 1, "admin": True}},
        [],
        [
            {"id": "e1", "title": "Raid", "capacity": 2, "members": []},
            {"id": "e2", "title": "Raid", "capacity": 3, "members": []},
        ],
    ),
    expected={
        "status": "ready",
        "command": {"tool": "create_event", "args": {"title": "Raid", "capacity": 1}},
        "errors": [],
    },
    description="Создание очищает title, игнорирует лишние поля и допускает существующие названия",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {
            "tool": "join_event",
            "args": {"member_name": "  Ira ", "event_title": "\tRaid\n", "capacity": 9},
        },
        [{"id": "m1", "name": "Ira"}, {"id": "m2", "name": "Max"}],
        [{"id": "e1", "title": "Raid", "capacity": 2, "members": ["m2"]}],
    ),
    expected={
        "status": "ready",
        "command": {"tool": "join_event", "args": {"member_id": "m1", "event_id": "e1"}},
        "errors": [],
    },
    description="Уникальные очищенные названия превращаются только в канонические ID",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"tool": "join_event", "args": {"member_name": "Ira", "event_title": "Moon"}},
        [{"id": "m1", "name": "Ira"}, {"id": "m2", "name": "Ira"}],
        [],
    ),
    expected={
        "status": "rejected",
        "command": None,
        "errors": ["ambiguous_member", "unknown_event"],
    },
    description="Независимые ошибки участника и события собираются в заданном порядке",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=({"tool": "create_event", "args": {"title": None, "capacity": True}}, [], []),
    expected={"status": "rejected", "command": None, "errors": ["title_empty", "invalid_capacity"]},
    description="None не является названием, а bool не является допустимой вместимостью",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=({"tool": "create_event", "args": {"title": 123, "capacity": 0}}, [], []),
    expected={"status": "rejected", "command": None, "errors": ["title_empty", "invalid_capacity"]},
    description="Нестроковое название и нулевая вместимость дают две ошибки",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=({"tool": "create_event", "args": {"capacity": 3.0}}, [], []),
    expected={"status": "rejected", "command": None, "errors": ["title_empty", "invalid_capacity"]},
    description="Отсутствующее название и float вместо int отклоняются",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=({"tool": "join_event", "args": {"event_title": None}}, [{"id": "m1", "name": "Ira"}], []),
    expected={
        "status": "rejected",
        "command": None,
        "errors": ["member_name_empty", "event_title_empty"],
    },
    description="Отсутствующее имя и None вместо события не запускают поиск пустых значений",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=({"tool": "join_event", "args": {"member_name": [], "event_title": " \t\n "}}, [], []),
    expected={
        "status": "rejected",
        "command": None,
        "errors": ["member_name_empty", "event_title_empty"],
    },
    description="Нестроковое имя и пробельное название события считаются пустыми",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"tool": "join_event", "args": {"member_name": "ira", "event_title": "Raid"}},
        [{"id": "m1", "name": "Ira"}],
        [
            {"id": "e1", "title": "Raid", "capacity": 1, "members": []},
            {"id": "e2", "title": "Raid", "capacity": 1, "members": []},
        ],
    ),
    expected={
        "status": "rejected",
        "command": None,
        "errors": ["unknown_member", "ambiguous_event"],
    },
    description="Регистр имени значим, неоднозначное событие проверяется независимо",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"tool": "join_event", "args": {"member_name": "Ira", "event_title": "Raid"}},
        [{"id": "m1", "name": "Ira"}],
        [{"id": "e1", "title": "Raid", "capacity": 1, "members": ["m1"]}],
    ),
    expected={"status": "rejected", "command": None, "errors": ["already_joined"]},
    description="Повторное вступление имеет приоритет перед заполненностью",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"tool": "join_event", "args": {"member_name": "Ira", "event_title": "Raid"}},
        [{"id": "m1", "name": "Ira"}],
        [{"id": "e1", "title": "Raid", "capacity": 1, "members": ["m2"]}],
    ),
    expected={"status": "rejected", "command": None, "errors": ["event_full"]},
    description="Заполненное событие отклоняет нового участника",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=({"tool": "remove_member", "args": {}}, [], []),
    expected={"status": "rejected", "command": None, "errors": ["unknown_tool"]},
    description="Неизвестный инструмент даёт только unknown_tool",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
def task_xla13_prepare_action(raw, members, events): ...
