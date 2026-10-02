from ego.testing import case


@case(
    args=(
        [
            {"id": "T", "role": "tank", "wait_seconds": 10},
            {"id": "B", "role": "damage", "wait_seconds": 20},
            {"id": "A", "role": "damage", "wait_seconds": 20},
        ],
        {"tank": 1, "healer": 1, "damage": 1},
    ),
    expected={
        "members": ["T", "A"],
        "missing": {"tank": 0, "healer": 1, "damage": 0},
        "ready": False,
    },
    description="Нехватка лекаря сохраняет частичный состав, равное ожидание решает ID",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "D", "role": "damage", "wait_seconds": 100},
            {"id": "H", "role": "healer", "wait_seconds": 20},
            {"id": "T", "role": "tank", "wait_seconds": 0},
        ],
        {"damage": 1, "healer": 1, "tank": 1},
    ),
    expected={
        "members": ["T", "H", "D"],
        "missing": {"tank": 0, "healer": 0, "damage": 0},
        "ready": True,
    },
    description="Готовый состав следует порядку ролей, а не очереди или ключей slots",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=([{"id": "T", "role": "tank", "wait_seconds": 100}], {}),
    expected={"members": [], "missing": {"tank": 0, "healer": 0, "damage": 0}, "ready": True},
    description="Пустой запрос мест уже готов и не выбирает кандидатов",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=([], {"tank": 2, "damage": 1}),
    expected={"members": [], "missing": {"tank": 2, "healer": 0, "damage": 1}, "ready": False},
    description="Пустая очередь возвращает точное число недостающих мест",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "T", "role": "tank", "wait_seconds": 1},
            {"id": "H", "role": "healer", "wait_seconds": 1},
            {"id": "D", "role": "damage", "wait_seconds": 1},
        ],
        {"tank": 0, "healer": 0, "damage": 0},
    ),
    expected={"members": [], "missing": {"tank": 0, "healer": 0, "damage": 0}, "ready": True},
    description="Явные нулевые места не заполняются",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "A", "role": "damage", "wait_seconds": 10},
            {"id": "Z", "role": "damage", "wait_seconds": 30},
            {"id": "B", "role": "damage", "wait_seconds": 30},
            {"id": "C", "role": "damage", "wait_seconds": 0},
        ],
        {"damage": 2},
    ),
    expected={
        "members": ["B", "Z"],
        "missing": {"tank": 0, "healer": 0, "damage": 0},
        "ready": True,
    },
    description="Сначала большее ожидание, затем меньший ID; лишние кандидаты не берутся",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "H2", "role": "healer", "wait_seconds": 10},
            {"id": "T2", "role": "tank", "wait_seconds": 5},
            {"id": "D", "role": "damage", "wait_seconds": 100},
            {"id": "T1", "role": "tank", "wait_seconds": 20},
            {"id": "H1", "role": "healer", "wait_seconds": 15},
        ],
        {"tank": 2, "healer": 2, "damage": 1},
    ),
    expected={
        "members": ["T1", "T2", "H1", "H2", "D"],
        "missing": {"tank": 0, "healer": 0, "damage": 0},
        "ready": True,
    },
    description="Несколько мест каждой роли сохраняют сортировку внутри своей роли",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "T", "role": "tank", "wait_seconds": 100},
            {"id": "H", "role": "healer", "wait_seconds": 100},
            {"id": "D", "role": "damage", "wait_seconds": 0},
        ],
        {"damage": 1},
    ),
    expected={"members": ["D"], "missing": {"tank": 0, "healer": 0, "damage": 0}, "ready": True},
    description="Отсутствующие роли в slots требуют ноль мест, но присутствуют в missing",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=([{"id": "H", "role": "healer", "wait_seconds": 2}], {"healer": 2}),
    expected={"members": ["H"], "missing": {"tank": 0, "healer": 1, "damage": 0}, "ready": False},
    description="Одного кандидата нельзя использовать дважды для одной роли",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "2", "role": "tank", "wait_seconds": 0},
            {"id": "10", "role": "tank", "wait_seconds": 0},
            {"id": "1", "role": "tank", "wait_seconds": 0},
        ],
        {"tank": 2},
    ),
    expected={
        "members": ["1", "10"],
        "missing": {"tank": 0, "healer": 0, "damage": 0},
        "ready": True,
    },
    description="ID являются строками: при нулевом ожидании используется алфавитный порядок",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
def task_xla08_build_party(players, slots): ...
