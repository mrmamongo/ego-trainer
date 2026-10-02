from ego.testing import case


CATALOG = [
    {"id": "q2", "title": "Волки", "min_level": 5, "zone": "forest"},
    {"id": "q1", "title": "Травы", "min_level": 2, "zone": "forest"},
    {"id": "q3", "title": "Рыба", "min_level": 1, "zone": "lake"},
]


@case(
    args=(CATALOG, {"q2": "active", "unknown": "completed"}, 2, "forest"),
    expected={"available": ["q1"], "active": ["q2"], "completed": []},
    description="Журнал объединяет каталог, прогресс, уровень и выбранную зону",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "done", "title": "Рейд", "min_level": 20, "zone": "forest"},
            {"id": "started", "title": "Дракон", "min_level": 30, "zone": "forest"},
        ],
        {"done": "completed", "started": "active"},
        0,
        "forest",
    ),
    expected={"available": [], "active": ["started"], "completed": ["done"]},
    description="Начатый и завершённый квесты видны даже при недостаточном уровне",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(CATALOG, {}, 2, "forest"),
    expected={"available": ["q1"], "active": [], "completed": []},
    description="Минимальный уровень включителен, более сложный квест скрыт",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=([], {"ghost": "active"}, 50, "forest"),
    expected={"available": [], "active": [], "completed": []},
    description="Пустой каталог всегда возвращает три пустые вкладки",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(CATALOG, {"q1": "active", "q2": "completed"}, 50, "desert"),
    expected={"available": [], "active": [], "completed": []},
    description="Неизвестная зона скрывает даже начатые квесты других зон",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(CATALOG, {"ghost": "active", "missing": "completed"}, 5, "forest"),
    expected={"available": ["q1", "q2"], "active": [], "completed": []},
    description="Прогресс неизвестных каталогу ID игнорируется",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "z", "title": "А", "min_level": 2, "zone": "forest"},
            {"id": "b", "title": "Б", "min_level": 1, "zone": "forest"},
            {"id": "a", "title": "Я", "min_level": 2, "zone": "forest"},
        ],
        {},
        2,
        "forest",
    ),
    expected={"available": ["b", "a", "z"], "active": [], "completed": []},
    description="Сортировка по min_level и id, название не влияет",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "z-active", "title": "А", "min_level": 9, "zone": "forest"},
            {"id": "z-done", "title": "Б", "min_level": 4, "zone": "forest"},
            {"id": "a-active", "title": "В", "min_level": 9, "zone": "forest"},
            {"id": "a-done", "title": "Г", "min_level": 4, "zone": "forest"},
            {"id": "low-active", "title": "Д", "min_level": 1, "zone": "forest"},
            {"id": "low-done", "title": "Е", "min_level": 2, "zone": "forest"},
        ],
        {
            "z-active": "active",
            "a-active": "active",
            "low-active": "active",
            "z-done": "completed",
            "a-done": "completed",
            "low-done": "completed",
        },
        0,
        "forest",
    ),
    expected={
        "available": [],
        "active": ["low-active", "a-active", "z-active"],
        "completed": ["low-done", "a-done", "z-done"],
    },
    description="Сортировка применяется отдельно к активным и завершённым вкладкам",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "lower", "title": "Лес", "min_level": 0, "zone": "forest"},
            {"id": "upper", "title": "Лес", "min_level": 0, "zone": "Forest"},
        ],
        {"upper": "completed"},
        0,
        "forest",
    ),
    expected={"available": ["lower"], "active": [], "completed": []},
    description="Зона сравнивается точно, с учётом регистра",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(CATALOG, {"q2": "active"}, 1, "forest"),
    expected={"available": [], "active": ["q2"], "completed": []},
    description="Неначатый квест на один уровень выше скрыт",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        [
            {"id": "q1", "title": "Первый", "min_level": 1, "zone": "start"},
            {"id": "q0", "title": "Обучение", "min_level": 0, "zone": "start"},
        ],
        {},
        0,
        "start",
    ),
    expected={"available": ["q0"], "active": [], "completed": []},
    description="Нулевой уровень допускает квест с min_level=0",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
def task_xla04_quest_journal(catalog, progress, player_level, zone): ...
