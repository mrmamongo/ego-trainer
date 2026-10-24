from ego.testing import case


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
        "ok": True,
    },
    description="Создание, вступление и объявление используют результаты предыдущих шагов",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"events": {}, "announcements": [], "next_id": 1},
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
        ],
    ),
    expected={
        "state": {
            "events": {"e1": {"title": "Raid", "capacity": 2, "members": []}},
            "announcements": [],
            "next_id": 2,
        },
        "steps": [
            {"id": "bad", "status": "rejected", "result": None, "reason": "unknown_event"},
            {"id": "create", "status": "done", "result": {"event_id": "e1"}, "reason": None},
        ],
        "ok": False,
    },
    description="Некритичный отказ позволяет выполнить следующий шаг, но ok остаётся False",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"events": {}, "announcements": [], "next_id": 1},
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
                "id": "announce",
                "tool": "prepare_announcement",
                "critical": False,
                "args": {"event_id": {"from_step": "create", "field": "event_id"}, "text": "Meet"},
            },
        ],
    ),
    expected={
        "state": {"events": {}, "announcements": [], "next_id": 1},
        "steps": [
            {"id": "bad", "status": "rejected", "result": None, "reason": "unknown_event"},
            {"id": "create", "status": "skipped", "result": None, "reason": "stopped_after:bad"},
            {"id": "announce", "status": "skipped", "result": None, "reason": "stopped_after:bad"},
        ],
        "ok": False,
    },
    description="Критичный отказ пропускает все оставшиеся шаги с одним stopped_after",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {
            "events": {"e4": {"title": "Raid", "capacity": 2, "members": ["X"]}},
            "announcements": [{"event_id": "e4", "text": "Before"}],
            "next_id": 5,
        },
        [],
    ),
    expected={
        "state": {
            "events": {"e4": {"title": "Raid", "capacity": 2, "members": ["X"]}},
            "announcements": [{"event_id": "e4", "text": "Before"}],
            "next_id": 5,
        },
        "steps": [],
        "ok": True,
    },
    description="Пустой план успешен и сохраняет исходное состояние",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"events": {}, "announcements": [], "next_id": 1},
        [
            {
                "id": "invalid",
                "tool": "create_event",
                "critical": False,
                "args": {"title": None, "capacity": 2},
            },
            {
                "id": "dependent",
                "tool": "join_event",
                "critical": False,
                "args": {
                    "event_id": {"from_step": "invalid", "field": "event_id"},
                    "member_id": "A",
                },
            },
            {
                "id": "create",
                "tool": "create_event",
                "critical": True,
                "args": {"title": "Raid", "capacity": 2},
            },
        ],
    ),
    expected={
        "state": {
            "events": {"e1": {"title": "Raid", "capacity": 2, "members": []}},
            "announcements": [],
            "next_id": 2,
        },
        "steps": [
            {"id": "invalid", "status": "rejected", "result": None, "reason": "invalid_title"},
            {
                "id": "dependent",
                "status": "rejected",
                "result": None,
                "reason": "dependency_failed:invalid",
            },
            {"id": "create", "status": "done", "result": {"event_id": "e1"}, "reason": None},
        ],
        "ok": False,
    },
    description="Ссылка на отказавшее действие отклоняется; дальнейшее создание не теряет ID",
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
                "id": "missing",
                "tool": "join_event",
                "critical": True,
                "args": {"event_id": {"from_step": "create", "field": "unknown"}, "member_id": "A"},
            },
            {
                "id": "announce",
                "tool": "prepare_announcement",
                "critical": False,
                "args": {"event_id": {"from_step": "create", "field": "event_id"}, "text": "Meet"},
            },
        ],
    ),
    expected={
        "state": {
            "events": {"e1": {"title": "Raid", "capacity": 2, "members": []}},
            "announcements": [],
            "next_id": 2,
        },
        "steps": [
            {"id": "create", "status": "done", "result": {"event_id": "e1"}, "reason": None},
            {
                "id": "missing",
                "status": "rejected",
                "result": None,
                "reason": "missing_result_field:create:unknown",
            },
            {
                "id": "announce",
                "status": "skipped",
                "result": None,
                "reason": "stopped_after:missing",
            },
        ],
        "ok": False,
    },
    description="Отсутствующее поле результата даёт отдельную ошибку и может остановить план",
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
                "id": "field_first",
                "tool": "join_event",
                "critical": False,
                "args": {
                    "member_id": {"from_step": "create", "field": "missing"},
                    "event_id": {"from_step": "bad", "field": "event_id"},
                },
            },
            {
                "id": "dependency_first",
                "tool": "join_event",
                "critical": False,
                "args": {
                    "event_id": {"from_step": "bad", "field": "event_id"},
                    "member_id": {"from_step": "create", "field": "missing"},
                },
            },
        ],
    ),
    expected={
        "state": {
            "events": {"e1": {"title": "Raid", "capacity": 2, "members": []}},
            "announcements": [],
            "next_id": 2,
        },
        "steps": [
            {"id": "create", "status": "done", "result": {"event_id": "e1"}, "reason": None},
            {"id": "bad", "status": "rejected", "result": None, "reason": "unknown_event"},
            {
                "id": "field_first",
                "status": "rejected",
                "result": None,
                "reason": "missing_result_field:create:missing",
            },
            {
                "id": "dependency_first",
                "status": "rejected",
                "result": None,
                "reason": "dependency_failed:bad",
            },
        ],
        "ok": False,
    },
    description="Первая ошибка ссылки определяется порядком вставки аргументов",
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
                "args": {"title": "Solo", "capacity": 1},
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
                "id": "repeat",
                "tool": "join_event",
                "critical": False,
                "args": {
                    "event_id": {"from_step": "create", "field": "event_id"},
                    "member_id": "Sam",
                },
            },
            {
                "id": "full",
                "tool": "join_event",
                "critical": False,
                "args": {
                    "event_id": {"from_step": "create", "field": "event_id"},
                    "member_id": "B",
                },
            },
        ],
    ),
    expected={
        "state": {
            "events": {"e1": {"title": "Solo", "capacity": 1, "members": ["Sam"]}},
            "announcements": [],
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
            {"id": "repeat", "status": "rejected", "result": None, "reason": "already_joined"},
            {"id": "full", "status": "rejected", "result": None, "reason": "event_full"},
        ],
        "ok": False,
    },
    description="Каждая команда видит изменения предыдущей; отказы не откатывают успех",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"events": {}, "announcements": [], "next_id": 4},
        [
            {
                "id": "first",
                "tool": "create_event",
                "critical": True,
                "args": {"title": " First ", "capacity": 1},
            },
            {
                "id": "second",
                "tool": "create_event",
                "critical": True,
                "args": {"title": "Second", "capacity": 2},
            },
            {
                "id": "join_first",
                "tool": "join_event",
                "critical": True,
                "args": {"event_id": {"from_step": "first", "field": "event_id"}, "member_id": "A"},
            },
            {
                "id": "announce_second",
                "tool": "prepare_announcement",
                "critical": True,
                "args": {
                    "event_id": {"from_step": "second", "field": "event_id"},
                    "text": " Next ",
                },
            },
        ],
    ),
    expected={
        "state": {
            "events": {
                "e4": {"title": "First", "capacity": 1, "members": ["A"]},
                "e5": {"title": "Second", "capacity": 2, "members": []},
            },
            "announcements": [{"event_id": "e5", "text": "Next"}],
            "next_id": 6,
        },
        "steps": [
            {"id": "first", "status": "done", "result": {"event_id": "e4"}, "reason": None},
            {"id": "second", "status": "done", "result": {"event_id": "e5"}, "reason": None},
            {
                "id": "join_first",
                "status": "done",
                "result": {"event_id": "e4", "member_id": "A"},
                "reason": None,
            },
            {
                "id": "announce_second",
                "status": "done",
                "result": {"announcement_index": 0},
                "reason": None,
            },
        ],
        "ok": True,
    },
    description="Несколько результатов хранятся по ID шага, включая не последний успех",
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
            {"id": "unknown", "tool": "missing_tool", "critical": True, "args": {}},
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
    ),
    expected={
        "state": {
            "events": {"e1": {"title": "Raid", "capacity": 2, "members": []}},
            "announcements": [],
            "next_id": 2,
        },
        "steps": [
            {"id": "create", "status": "done", "result": {"event_id": "e1"}, "reason": None},
            {"id": "unknown", "status": "rejected", "result": None, "reason": "unknown_tool"},
            {"id": "join", "status": "skipped", "result": None, "reason": "stopped_after:unknown"},
        ],
        "ok": False,
    },
    description="Поздний критичный отказ сохраняет уже созданное событие",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"events": {}, "announcements": [], "next_id": 1},
        [
            {
                "id": "capacity",
                "tool": "create_event",
                "critical": False,
                "args": {"title": "Wrong", "capacity": True},
            },
            {
                "id": "create",
                "tool": "create_event",
                "critical": True,
                "args": {"title": "Raid", "capacity": 2},
            },
        ],
    ),
    expected={
        "state": {
            "events": {"e1": {"title": "Raid", "capacity": 2, "members": []}},
            "announcements": [],
            "next_id": 2,
        },
        "steps": [
            {"id": "capacity", "status": "rejected", "result": None, "reason": "invalid_capacity"},
            {"id": "create", "status": "done", "result": {"event_id": "e1"}, "reason": None},
        ],
        "ok": False,
    },
    description="Предметная проверка GIVEN отклоняет bool, не расходуя следующий ID",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
def task_xla26_run_plan(state, steps): ...
