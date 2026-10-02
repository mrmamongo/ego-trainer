from ego.testing import case


@case(
    args=({"theme": "dark", "games": {"rank": 2}}, ["theme"]),
    expected={"profile": {"games": {"rank": 2}}, "removed_paths": [["theme"]]},
    description="Старый сценарий удаления листа верхнего уровня сохраняется",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {
            "games": {"preferences": {"sound": False, "mode": "solo"}, "rank": 0},
            "llm": {"language": "ru"},
        },
        ["games", "preferences"],
    ),
    expected={
        "profile": {"games": {"rank": 0}, "llm": {"language": "ru"}},
        "removed_paths": [["games", "preferences", "mode"], ["games", "preferences", "sound"]],
    },
    description="Вложенная ветка удаляется целиком, её листья сортируются",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({"games": {"x": None}}, ["games", "x"]),
    expected={"profile": {}, "removed_paths": [["games", "x"]]},
    description="Удаление последнего None-листа убирает опустевшего предка",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({"empty": {}, "games": {"rank": 0}}, ["missing"]),
    expected={"profile": {"empty": {}, "games": {"rank": 0}}, "removed_paths": []},
    description="Неизвестный корневой путь сохраняет даже пустые соседние ветки",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({"games": {"rank": 0}, "role": "tank"}, ["games", "rank", "value"]),
    expected={"profile": {"games": {"rank": 0}, "role": "tank"}, "removed_paths": []},
    description="Scalar на промежуточном шаге оставляет профиль прежним",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({"z": {"flag": False, "empty": {}, "count": 0}, "a": None, "middle": "text"}, []),
    expected={"profile": {}, "removed_paths": [["a"], ["middle"], ["z", "count"], ["z", "flag"]]},
    description="Пустой путь очищает корень и сообщает все scalar листья в порядке ключей",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({"keep_empty": {}, "games": {"preferences": {}}}, ["games", "preferences"]),
    expected={"profile": {"keep_empty": {}}, "removed_paths": []},
    description="Удаление пустой ветки не создаёт пути, но убирает только её пустых предков",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({}, []),
    expected={"profile": {}, "removed_paths": []},
    description="Очистка пустого профиля допустима",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({"games": {}, "keep": 1}, ["games", "missing"]),
    expected={"profile": {"games": {}, "keep": 1}, "removed_paths": []},
    description="Отсутствующий вложенный путь не приводит к очистке существующего пустого предка",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"games": {"preferences": {"x": 1}, "empty_sibling": {}}, "other": {"value": 2}},
        ["games", "preferences", "x"],
    ),
    expected={
        "profile": {"games": {"empty_sibling": {}}, "other": {"value": 2}},
        "removed_paths": [["games", "preferences", "x"]],
    },
    description="Очистка прекращается у предка с сохранившимся пустым соседом",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({"topic": {"z": {"b": 0, "a": False}, "a": None, "empty": {}}, "keep": True}, ["topic"]),
    expected={
        "profile": {"keep": True},
        "removed_paths": [["topic", "a"], ["topic", "z", "a"], ["topic", "z", "b"]],
    },
    description="Рекурсивный обход сортирует каждый уровень и сохраняет полные пути",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
def task_xla24_forget_topic(profile, path): ...
