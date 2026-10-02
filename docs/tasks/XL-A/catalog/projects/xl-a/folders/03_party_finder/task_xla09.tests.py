from ego.testing import case


@case(
    args=(
        [
            {"ticket_id": "r1", "player_id": "A", "role": "tank", "wait_seconds": 30},
            {"ticket_id": "r2", "player_id": "A", "role": "tank", "wait_seconds": 30},
        ],
        {"tank": 2},
    ),
    expected={"members": ["A"], "missing": {"tank": 1, "healer": 0, "damage": 0}, "ready": False},
    description="Две заявки одного игрока занимают только одно место",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"ticket_id": "r1", "player_id": "A", "role": "tank", "wait_seconds": 30},
            {"ticket_id": "r2", "player_id": "B", "role": "tank", "wait_seconds": 20},
            {"ticket_id": "r3", "player_id": "A", "role": "tank", "wait_seconds": 30},
            {"ticket_id": "r4", "player_id": "C", "role": "tank", "wait_seconds": 10},
            {"ticket_id": "r5", "player_id": "A", "role": "tank", "wait_seconds": 30},
        ],
        {"tank": 2},
    ),
    expected={
        "members": ["A", "B"],
        "missing": {"tank": 0, "healer": 0, "damage": 0},
        "ready": True,
    },
    description="Три несоседние заявки одного игрока не вытесняют второго игрока",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"ticket_id": "r1", "player_id": "D", "role": "damage", "wait_seconds": 100},
            {"ticket_id": "r2", "player_id": "H", "role": "healer", "wait_seconds": 50},
            {"ticket_id": "r3", "player_id": "T", "role": "tank", "wait_seconds": 1},
        ],
        {"damage": 1, "healer": 1, "tank": 1},
    ),
    expected={
        "members": ["T", "H", "D"],
        "missing": {"tank": 0, "healer": 0, "damage": 0},
        "ready": True,
    },
    description="Очередь без повторов сохраняет порядок ролей и готовность",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"ticket_id": "r1", "player_id": "A", "role": "tank", "wait_seconds": 30},
            {"ticket_id": "r2", "player_id": "A", "role": "tank", "wait_seconds": 30},
        ],
        {},
    ),
    expected={"members": [], "missing": {"tank": 0, "healer": 0, "damage": 0}, "ready": True},
    description="Пустой запрос мест готов даже при повторных заявках",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=([], {"tank": 1, "healer": 2, "damage": 3}),
    expected={"members": [], "missing": {"tank": 1, "healer": 2, "damage": 3}, "ready": False},
    description="Пустая очередь заявок возвращает все недостающие места",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"ticket_id": "a-ticket", "player_id": "Z", "role": "damage", "wait_seconds": 10},
            {"ticket_id": "z-ticket", "player_id": "A", "role": "damage", "wait_seconds": 10},
        ],
        {"damage": 1},
    ),
    expected={"members": ["A"], "missing": {"tank": 0, "healer": 0, "damage": 0}, "ready": True},
    description="При равном ожидании сравнивается player_id, а не ticket_id",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"ticket_id": "r1", "player_id": "H", "role": "healer", "wait_seconds": 0},
            {"ticket_id": "r2", "player_id": "H", "role": "healer", "wait_seconds": 0},
            {"ticket_id": "r3", "player_id": "H", "role": "healer", "wait_seconds": 0},
        ],
        {"healer": 2},
    ),
    expected={"members": ["H"], "missing": {"tank": 0, "healer": 1, "damage": 0}, "ready": False},
    description="Три одинаковые заявки лекаря дают одного уникального участника",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"ticket_id": "r1", "player_id": "D", "role": "damage", "wait_seconds": 100},
            {"ticket_id": "r2", "player_id": "T", "role": "tank", "wait_seconds": 10},
            {"ticket_id": "r3", "player_id": "H", "role": "healer", "wait_seconds": 20},
            {"ticket_id": "r4", "player_id": "D", "role": "damage", "wait_seconds": 100},
            {"ticket_id": "r5", "player_id": "T", "role": "tank", "wait_seconds": 10},
            {"ticket_id": "r6", "player_id": "H", "role": "healer", "wait_seconds": 20},
        ],
        {"tank": 1, "healer": 1, "damage": 1},
    ),
    expected={
        "members": ["T", "H", "D"],
        "missing": {"tank": 0, "healer": 0, "damage": 0},
        "ready": True,
    },
    description="Повторы удаляются для всех ролей без изменения порядка состава",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"ticket_id": "r1", "player_id": "A", "role": "damage", "wait_seconds": 30},
            {"ticket_id": "r2", "player_id": "A", "role": "damage", "wait_seconds": 30},
            {"ticket_id": "r3", "player_id": "B", "role": "damage", "wait_seconds": 20},
        ],
        {"damage": 4},
    ),
    expected={
        "members": ["A", "B"],
        "missing": {"tank": 0, "healer": 0, "damage": 2},
        "ready": False,
    },
    description="Дефицит считается по уникальным игрокам, частичный состав сохраняется",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"ticket_id": "r5", "player_id": "A", "role": "tank", "wait_seconds": 30},
            {"ticket_id": "r4", "player_id": "C", "role": "tank", "wait_seconds": 10},
            {"ticket_id": "r3", "player_id": "A", "role": "tank", "wait_seconds": 30},
            {"ticket_id": "r2", "player_id": "B", "role": "tank", "wait_seconds": 20},
            {"ticket_id": "r1", "player_id": "A", "role": "tank", "wait_seconds": 30},
        ],
        {"tank": 2},
    ),
    expected={
        "members": ["A", "B"],
        "missing": {"tank": 0, "healer": 0, "damage": 0},
        "ready": True,
    },
    description="Перестановка одинаковых по смыслу заявок не меняет подбор",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"ticket_id": "r1", "player_id": "T", "role": "tank", "wait_seconds": 100},
            {"ticket_id": "r2", "player_id": "T", "role": "tank", "wait_seconds": 100},
            {"ticket_id": "r3", "player_id": "D", "role": "damage", "wait_seconds": 0},
            {"ticket_id": "r4", "player_id": "H", "role": "healer", "wait_seconds": 50},
        ],
        {"tank": 0, "damage": 1},
    ),
    expected={"members": ["D"], "missing": {"tank": 0, "healer": 0, "damage": 0}, "ready": True},
    description="Нулевые и отсутствующие роли не выбираются, все ключи missing остаются",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
def task_xla09_party_from_tickets(tickets, slots): ...
