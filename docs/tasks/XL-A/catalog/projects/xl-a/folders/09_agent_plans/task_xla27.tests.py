from ego.testing import case


@case(
    args=(
        {
            "events": {"e1": {"title": "Raid", "capacity": 2, "members": []}},
            "announcements": [],
            "next_id": 2,
        },
        [
            {
                "id": "create",
                "tool": "create_event",
                "critical": True,
                "args": {"title": "Raid", "capacity": 2},
            },
            {
                "id": "join",
                "tool": "join_event",
                "critical": True,
                "args": {
                    "event_id": {"from_step": "create", "field": "event_id"},
                    "member_id": "B",
                },
            },
        ],
        {"create": {"event_id": "e1"}},
    ),
    expected={
        "state": {
            "events": {"e1": {"title": "Raid", "capacity": 2, "members": ["B"]}},
            "announcements": [],
            "next_id": 2,
        },
        "steps": [
            {"id": "create", "status": "reused", "result": {"event_id": "e1"}, "reason": None},
            {
                "id": "join",
                "status": "done",
                "result": {"event_id": "e1", "member_id": "B"},
                "reason": None,
            },
        ],
        "completed": {"create": {"event_id": "e1"}, "join": {"event_id": "e1", "member_id": "B"}},
        "ok": True,
    },
    description="Кешированное создание не расходует ID, следующий шаг использует сохранённый event_id",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {
            "events": {"e1": {"title": "Raid", "capacity": 2, "members": ["B"]}},
            "announcements": [],
            "next_id": 2,
        },
        [
            {
                "id": "create",
                "tool": "create_event",
                "critical": True,
                "args": {"title": "Raid", "capacity": 2},
            },
            {
                "id": "join",
                "tool": "join_event",
                "critical": True,
                "args": {
                    "event_id": {"from_step": "create", "field": "event_id"},
                    "member_id": "B",
                },
            },
        ],
        {"create": {"event_id": "e1"}, "join": {"event_id": "e1", "member_id": "B"}},
    ),
    expected={
        "state": {
            "events": {"e1": {"title": "Raid", "capacity": 2, "members": ["B"]}},
            "announcements": [],
            "next_id": 2,
        },
        "steps": [
            {"id": "create", "status": "reused", "result": {"event_id": "e1"}, "reason": None},
            {
                "id": "join",
                "status": "reused",
                "result": {"event_id": "e1", "member_id": "B"},
                "reason": None,
            },
        ],
        "completed": {"create": {"event_id": "e1"}, "join": {"event_id": "e1", "member_id": "B"}},
        "ok": True,
    },
    description="Повтор успешного продолжения переиспользует все шаги и не дублирует участника",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {
            "events": {"e1": {"title": "Raid", "capacity": 2, "members": []}},
            "announcements": [{"event_id": "e1", "text": "Meet"}],
            "next_id": 2,
        },
        [
            {
                "id": "announce",
                "tool": "prepare_announcement",
                "critical": False,
                "args": {"event_id": "e1", "text": "Meet"},
            }
        ],
        {"announce": {"announcement_index": 0}},
    ),
    expected={
        "state": {
            "events": {"e1": {"title": "Raid", "capacity": 2, "members": []}},
            "announcements": [{"event_id": "e1", "text": "Meet"}],
            "next_id": 2,
        },
        "steps": [
            {
                "id": "announce",
                "status": "reused",
                "result": {"announcement_index": 0},
                "reason": None,
            }
        ],
        "completed": {"announce": {"announcement_index": 0}},
        "ok": True,
    },
    description="Кешированное объявление не добавляется второй раз",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=({"events": {}, "announcements": [], "next_id": 1}, [], {}),
    expected={
        "state": {"events": {}, "announcements": [], "next_id": 1},
        "steps": [],
        "completed": {},
        "ok": True,
    },
    description="Пустой план и пустой кеш успешны",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"events": {}, "announcements": [], "next_id": 1},
        [
            {
                "id": "create",
                "tool": "create_event",
                "critical": True,
                "args": {"title": "Raid", "capacity": 2},
            },
            {
                "id": "join",
                "tool": "join_event",
                "critical": True,
                "args": {
                    "event_id": {"from_step": "create", "field": "event_id"},
                    "member_id": "Sam",
                },
            },
            {
                "id": "announce",
                "tool": "prepare_announcement",
                "critical": False,
                "args": {"event_id": {"from_step": "create", "field": "event_id"}, "text": "Meet"},
            },
        ],
        {},
    ),
    expected={
        "state": {
            "events": {"e1": {"title": "Raid", "capacity": 2, "members": ["Sam"]}},
            "announcements": [{"event_id": "e1", "text": "Meet"}],
            "next_id": 2,
        },
        "steps": [
            {"id": "create", "status": "done", "result": {"event_id": "e1"}, "reason": None},
            {
                "id": "join",
                "status": "done",
                "result": {"event_id": "e1", "member_id": "Sam"},
                "reason": None,
            },
            {
                "id": "announce",
                "status": "done",
                "result": {"announcement_index": 0},
                "reason": None,
            },
        ],
        "completed": {
            "create": {"event_id": "e1"},
            "join": {"event_id": "e1", "member_id": "Sam"},
            "announce": {"announcement_index": 0},
        },
        "ok": True,
    },
    description="Без кеша выполняется весь план, новые результаты доступны ссылкам и сохраняются",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {
            "events": {"e1": {"title": "Raid", "capacity": 2, "members": []}},
            "announcements": [],
            "next_id": 2,
        },
        [
            {
                "id": "bad",
                "tool": "join_event",
                "critical": False,
                "args": {"event_id": "e9", "member_id": "Sam"},
            },
            {
                "id": "create",
                "tool": "create_event",
                "critical": True,
                "args": {"title": "Raid", "capacity": 2},
            },
            {
                "id": "join",
                "tool": "join_event",
                "critical": True,
                "args": {
                    "event_id": {"from_step": "create", "field": "event_id"},
                    "member_id": "Sam",
                },
            },
        ],
        {"create": {"event_id": "e1"}},
    ),
    expected={
        "state": {
            "events": {"e1": {"title": "Raid", "capacity": 2, "members": ["Sam"]}},
            "announcements": [],
            "next_id": 2,
        },
        "steps": [
            {"id": "bad", "status": "rejected", "result": None, "reason": "unknown_event"},
            {"id": "create", "status": "reused", "result": {"event_id": "e1"}, "reason": None},
            {
                "id": "join",
                "status": "done",
                "result": {"event_id": "e1", "member_id": "Sam"},
                "reason": None,
            },
        ],
        "completed": {"create": {"event_id": "e1"}, "join": {"event_id": "e1", "member_id": "Sam"}},
        "ok": False,
    },
    description="Сохранённый шаг после раннего некритичного отказа переиспользуется; отказ не кешируется",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {
            "events": {"e1": {"title": "Raid", "capacity": 2, "members": []}},
            "announcements": [],
            "next_id": 2,
        },
        [
            {
                "id": "bad",
                "tool": "join_event",
                "critical": True,
                "args": {"event_id": "e9", "member_id": "Sam"},
            },
            {
                "id": "create",
                "tool": "create_event",
                "critical": True,
                "args": {"title": "Raid", "capacity": 2},
            },
            {
                "id": "join",
                "tool": "join_event",
                "critical": True,
                "args": {
                    "event_id": {"from_step": "create", "field": "event_id"},
                    "member_id": "Sam",
                },
            },
        ],
        {"create": {"event_id": "e1"}},
    ),
    expected={
        "state": {
            "events": {"e1": {"title": "Raid", "capacity": 2, "members": []}},
            "announcements": [],
            "next_id": 2,
        },
        "steps": [
            {"id": "bad", "status": "rejected", "result": None, "reason": "unknown_event"},
            {"id": "create", "status": "skipped", "result": None, "reason": "stopped_after:bad"},
            {"id": "join", "status": "skipped", "result": None, "reason": "stopped_after:bad"},
        ],
        "completed": {"create": {"event_id": "e1"}},
        "ok": False,
    },
    description="Новый критичный отказ пропускает даже кешированный шаг и сохраняет уже созданное состояние",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {
            "events": {"e1": {"title": "Raid", "capacity": 2, "members": []}},
            "announcements": [{"event_id": "e1", "text": "Meet"}],
            "next_id": 2,
        },
        [
            {
                "id": "create",
                "tool": "create_event",
                "critical": True,
                "args": {"title": "Raid", "capacity": 2},
            },
            {
                "id": "missing",
                "tool": "join_event",
                "critical": True,
                "args": {"event_id": {"from_step": "create", "field": "absent"}, "member_id": "A"},
            },
            {
                "id": "announce",
                "tool": "prepare_announcement",
                "critical": False,
                "args": {"event_id": {"from_step": "create", "field": "event_id"}, "text": "Meet"},
            },
        ],
        {"create": {"event_id": "e1"}, "announce": {"announcement_index": 0}},
    ),
    expected={
        "state": {
            "events": {"e1": {"title": "Raid", "capacity": 2, "members": []}},
            "announcements": [{"event_id": "e1", "text": "Meet"}],
            "next_id": 2,
        },
        "steps": [
            {"id": "create", "status": "reused", "result": {"event_id": "e1"}, "reason": None},
            {
                "id": "missing",
                "status": "rejected",
                "result": None,
                "reason": "missing_result_field:create:absent",
            },
            {
                "id": "announce",
                "status": "skipped",
                "result": None,
                "reason": "stopped_after:missing",
            },
        ],
        "completed": {"create": {"event_id": "e1"}, "announce": {"announcement_index": 0}},
        "ok": False,
    },
    description="Отсутствующее поле кешированного результата останавливает план без очистки кеша",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"events": {}, "announcements": [], "next_id": 1},
        [
            {
                "id": "create",
                "tool": "create_event",
                "critical": True,
                "args": {"title": "Raid", "capacity": 2},
            },
            {
                "id": "bad",
                "tool": "join_event",
                "critical": False,
                "args": {"event_id": "e9", "member_id": "Sam"},
            },
            {
                "id": "announce",
                "tool": "prepare_announcement",
                "critical": False,
                "args": {"event_id": {"from_step": "create", "field": "event_id"}, "text": "Meet"},
            },
        ],
        {},
    ),
    expected={
        "state": {
            "events": {"e1": {"title": "Raid", "capacity": 2, "members": []}},
            "announcements": [{"event_id": "e1", "text": "Meet"}],
            "next_id": 2,
        },
        "steps": [
            {"id": "create", "status": "done", "result": {"event_id": "e1"}, "reason": None},
            {"id": "bad", "status": "rejected", "result": None, "reason": "unknown_event"},
            {
                "id": "announce",
                "status": "done",
                "result": {"announcement_index": 0},
                "reason": None,
            },
        ],
        "completed": {"create": {"event_id": "e1"}, "announce": {"announcement_index": 0}},
        "ok": False,
    },
    description="Новые успехи до и после отказа сохраняются, разрозненный кеш допустим",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {
            "events": {"e1": {"title": "Raid", "capacity": 2, "members": []}},
            "announcements": [{"event_id": "e1", "text": "Meet"}],
            "next_id": 2,
        },
        [
            {
                "id": "announce",
                "tool": "prepare_announcement",
                "critical": False,
                "args": {"event_id": "e1", "text": "Meet"},
            },
            {
                "id": "zero",
                "tool": "create_event",
                "critical": False,
                "args": {
                    "title": "Index",
                    "capacity": {"from_step": "announce", "field": "announcement_index"},
                },
            },
            {
                "id": "fresh",
                "tool": "create_event",
                "critical": True,
                "args": {"title": "Fresh", "capacity": 1},
            },
        ],
        {"announce": {"announcement_index": 0}},
    ),
    expected={
        "state": {
            "events": {
                "e1": {"title": "Raid", "capacity": 2, "members": []},
                "e2": {"title": "Fresh", "capacity": 1, "members": []},
            },
            "announcements": [{"event_id": "e1", "text": "Meet"}],
            "next_id": 3,
        },
        "steps": [
            {
                "id": "announce",
                "status": "reused",
                "result": {"announcement_index": 0},
                "reason": None,
            },
            {"id": "zero", "status": "rejected", "result": None, "reason": "invalid_capacity"},
            {"id": "fresh", "status": "done", "result": {"event_id": "e2"}, "reason": None},
        ],
        "completed": {"announce": {"announcement_index": 0}, "fresh": {"event_id": "e2"}},
        "ok": False,
    },
    description="Нулевое поле кеша существует: его проверяет команда; отказ не расходует ID",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"events": {}, "announcements": [], "next_id": 1},
        [
            {"id": "bad", "tool": "unknown", "critical": False, "args": {}},
            {
                "id": "dependent",
                "tool": "join_event",
                "critical": False,
                "args": {"event_id": {"from_step": "bad", "field": "event_id"}, "member_id": "A"},
            },
            {
                "id": "create",
                "tool": "create_event",
                "critical": True,
                "args": {"title": "Raid", "capacity": 2},
            },
        ],
        {},
    ),
    expected={
        "state": {
            "events": {"e1": {"title": "Raid", "capacity": 2, "members": []}},
            "announcements": [],
            "next_id": 2,
        },
        "steps": [
            {"id": "bad", "status": "rejected", "result": None, "reason": "unknown_tool"},
            {
                "id": "dependent",
                "status": "rejected",
                "result": None,
                "reason": "dependency_failed:bad",
            },
            {"id": "create", "status": "done", "result": {"event_id": "e1"}, "reason": None},
        ],
        "completed": {"create": {"event_id": "e1"}},
        "ok": False,
    },
    description="Отказ команды и зависимый отказ не попадают в completed, независимый шаг выполняется",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {
            "events": {"e1": {"title": "Raid", "capacity": 2, "members": ["Sam"]}},
            "announcements": [{"event_id": "e1", "text": "Meet"}],
            "next_id": 2,
        },
        [
            {
                "id": "join",
                "tool": "join_event",
                "critical": False,
                "args": {"event_id": "e1", "member_id": "Sam"},
            },
            {
                "id": "announce",
                "tool": "prepare_announcement",
                "critical": False,
                "args": {
                    "event_id": {"from_step": "join", "field": "event_id"},
                    "text": "Meet",
                },
            },
        ],
        {"announce": {"announcement_index": 0}},
    ),
    expected={
        "state": {
            "events": {"e1": {"title": "Raid", "capacity": 2, "members": ["Sam"]}},
            "announcements": [{"event_id": "e1", "text": "Meet"}],
            "next_id": 2,
        },
        "steps": [
            {"id": "join", "status": "rejected", "result": None, "reason": "already_joined"},
            {
                "id": "announce",
                "status": "reused",
                "result": {"announcement_index": 0},
                "reason": None,
            },
        ],
        "completed": {"announce": {"announcement_index": 0}},
        "ok": False,
    },
    description=(
        "Sam и объявление уже есть в состоянии, но сохранён только поздний успех: "
        "после некритичного already_joined кешированный шаг не разрешает ссылку заново"
    ),
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
def task_xla27_resume_plan(state, steps, completed): ...
