from ego.testing import case


PLAYERS = [
    {"id": "A", "level": 12, "role": "tank", "languages": ["en"], "online": True},
    {"id": "B", "level": 15, "role": "tank", "languages": ["ru", "en"], "online": True},
    {"id": "C", "level": 20, "role": "healer", "languages": ["ru"], "online": False},
]


@case(
    args=(PLAYERS, 12, "tank", "ru"),
    expected=["B"],
    description="Новый фильтр языка исключает кандидата с неподходящим языком",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(PLAYERS, 12, "tank"),
    expected=["A", "B"],
    description="Вызов со старым набором аргументов сохраняет поведение",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "offline", "level": 30, "role": "tank", "languages": ["ru"], "online": False},
            {"id": "low", "level": 11, "role": "tank", "languages": ["ru"], "online": True},
            {"id": "healer", "level": 20, "role": "healer", "languages": ["ru"], "online": True},
            {"id": "ok", "level": 12, "role": "tank", "languages": ["ru"], "online": True},
        ],
        12,
        "tank",
        "ru",
    ),
    expected=["ok"],
    description="Совпадение языка не отменяет online, уровень и роль",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=([], 0),
    expected=[],
    description="Пустой список игроков",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "Z", "level": 0, "role": "damage", "languages": [], "online": True},
            {"id": "A", "level": 5, "role": "tank", "languages": ["en"], "online": True},
            {"id": "M", "level": 2, "role": "healer", "languages": ["ru"], "online": True},
        ],
        0,
    ),
    expected=["Z", "A", "M"],
    description="По умолчанию разрешены все роли и языки, порядок исходный",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "below", "level": 11, "role": "damage", "languages": ["en"], "online": True},
            {"id": "equal", "level": 12, "role": "healer", "languages": ["en"], "online": True},
            {"id": "above", "level": 13, "role": "tank", "languages": ["en"], "online": True},
        ],
        12,
        None,
        "en",
    ),
    expected=["equal", "above"],
    description="Граница минимального уровня включительна при свободной роли",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "empty", "level": 1, "role": "healer", "languages": [], "online": True},
            {"id": "known", "level": 1, "role": "healer", "languages": ["ru"], "online": True},
        ],
        1,
        "healer",
        None,
    ),
    expected=["empty", "known"],
    description="Пустые languages допустимы без конкретного фильтра языка",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "empty", "level": 1, "role": "healer", "languages": [], "online": True},
            {"id": "known", "level": 1, "role": "healer", "languages": ["ru"], "online": True},
        ],
        1,
        "healer",
        "ru",
    ),
    expected=["known"],
    description="Пустые languages не совпадают с конкретным языком",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(PLAYERS, 0, None, "zz"),
    expected=[],
    description="Неизвестный код языка даёт пустой результат",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "upper", "level": 5, "role": "tank", "languages": ["RU"], "online": True},
            {"id": "long", "level": 5, "role": "tank", "languages": ["russian"], "online": True},
            {"id": "exact", "level": 5, "role": "tank", "languages": ["en", "ru"], "online": True},
        ],
        5,
        None,
        "ru",
    ),
    expected=["exact"],
    description="Код языка сравнивается точно, без подстрок и смены регистра",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "Z", "level": 9, "role": "damage", "languages": ["ru"], "online": True},
            {"id": "A", "level": 100, "role": "damage", "languages": ["ru"], "online": True},
            {"id": "M", "level": 9, "role": "damage", "languages": ["ru"], "online": False},
            {"id": "B", "level": 10, "role": "damage", "languages": ["ru"], "online": True},
        ],
        9,
        "damage",
        "ru",
    ),
    expected=["Z", "A", "B"],
    description="Отбор не сортирует найденных по ID или уровню",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
def task_xla07_find_candidates(players, min_level, role=None, language=None): ...
