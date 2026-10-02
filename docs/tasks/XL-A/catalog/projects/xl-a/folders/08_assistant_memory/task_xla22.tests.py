from ego.testing import case


@case(
    args=(
        {"role": "tank"},
        [{"path": ["role"], "value": "healer"}, {"path": ["llm", "language"], "value": "ru"}],
    ),
    expected={
        "profile": {"role": "healer", "llm": {"language": "ru"}},
        "changes": [
            {"path": ["role"], "kind": "changed", "before": "tank", "after": "healer"},
            {"path": ["llm", "language"], "kind": "added", "before": None, "after": "ru"},
        ],
        "errors": [],
    },
    description="Изменение листа и добавление отсутствующей ветки",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"role": "healer"},
        [
            {"path": ["role"], "value": "healer"},
            {"path": ["role", "name"], "value": "Mira"},
            {"path": ["theme"], "value": "dark"},
        ],
    ),
    expected={
        "profile": {"role": "healer", "theme": "dark"},
        "changes": [{"path": ["theme"], "kind": "added", "before": None, "after": "dark"}],
        "errors": [{"index": 1, "path": ["role", "name"], "reason": "path_conflict"}],
    },
    description="Повтор значения пропускается, конфликт не мешает следующей правке",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"known": None},
        [
            {"path": ["missing"], "value": None},
            {"path": ["known"], "value": "yes"},
            {"path": ["missing"], "value": None},
        ],
    ),
    expected={
        "profile": {"known": "yes", "missing": None},
        "changes": [
            {"path": ["missing"], "kind": "added", "before": None, "after": None},
            {"path": ["known"], "kind": "changed", "before": None, "after": "yes"},
        ],
        "errors": [],
    },
    description="Отсутствующий ключ отличается от существующего None через kind",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"yes": True, "zero": 0},
        [{"path": ["yes"], "value": 1}, {"path": ["zero"], "value": False}],
    ),
    expected={
        "profile": {"yes": 1, "zero": False},
        "changes": [
            {"path": ["yes"], "kind": "changed", "before": True, "after": 1},
            {"path": ["zero"], "kind": "changed", "before": 0, "after": False},
        ],
        "errors": [],
    },
    description="Равные по == bool и int считаются разными значениями",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"nested": {"x": 1}, "empty": {}},
        [
            {"path": ["nested"], "value": 5},
            {"path": ["empty"], "value": 0},
            {"path": ["good"], "value": 2},
        ],
    ),
    expected={
        "profile": {"nested": {"x": 1}, "empty": {}, "good": 2},
        "changes": [{"path": ["good"], "kind": "added", "before": None, "after": 2}],
        "errors": [
            {"index": 0, "path": ["nested"], "reason": "path_conflict"},
            {"index": 1, "path": ["empty"], "reason": "path_conflict"},
        ],
    },
    description="Заполненный и пустой словарь нельзя заменить scalar",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"false": False, "zero": 0, "none": None},
        [
            {"path": ["false", "x"], "value": 1},
            {"path": ["zero", "y"], "value": 2},
            {"path": ["none", "z"], "value": 3},
        ],
    ),
    expected={
        "profile": {"false": False, "zero": 0, "none": None},
        "changes": [],
        "errors": [
            {"index": 0, "path": ["false", "x"], "reason": "path_conflict"},
            {"index": 1, "path": ["zero", "y"], "reason": "path_conflict"},
            {"index": 2, "path": ["none", "z"], "reason": "path_conflict"},
        ],
    },
    description="Ложные scalar значения тоже блокируют промежуточный путь",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {},
        [
            {"path": ["count"], "value": 1},
            {"path": ["count"], "value": 2},
            {"path": ["count"], "value": 2},
            {"path": ["count"], "value": None},
        ],
    ),
    expected={
        "profile": {"count": None},
        "changes": [
            {"path": ["count"], "kind": "added", "before": None, "after": 1},
            {"path": ["count"], "kind": "changed", "before": 1, "after": 2},
            {"path": ["count"], "kind": "changed", "before": 2, "after": None},
        ],
        "errors": [],
    },
    description="Повторные пути выполняются последовательно и не объединяются",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {"untouched": {"empty": {}, "value": 7}},
        [{"path": ["a", "b", "c"], "value": False}, {"path": ["a", "b", "d"], "value": 0}],
    ),
    expected={
        "profile": {"untouched": {"empty": {}, "value": 7}, "a": {"b": {"c": False, "d": 0}}},
        "changes": [
            {"path": ["a", "b", "c"], "kind": "added", "before": None, "after": False},
            {"path": ["a", "b", "d"], "kind": "added", "before": None, "after": 0},
        ],
        "errors": [],
    },
    description="Создаётся несколько промежуточных словарей, соседние ветки независимы",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({"llm": {"language": "ru", "nested": {"v": None}}}, []),
    expected={
        "profile": {"llm": {"language": "ru", "nested": {"v": None}}},
        "changes": [],
        "errors": [],
    },
    description="Пустой пакет возвращает независимый глубокий снимок",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=({}, []),
    expected={"profile": {}, "changes": [], "errors": []},
    description="Пустой профиль и пустой пакет допустимы",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
@case(
    args=(
        {},
        [
            {"path": ["llm", "language"], "value": "ru"},
            {"path": ["llm", "language", "code"], "value": "en"},
            {"path": ["llm", "mode"], "value": "brief"},
        ],
    ),
    expected={
        "profile": {"llm": {"language": "ru", "mode": "brief"}},
        "changes": [
            {"path": ["llm", "language"], "kind": "added", "before": None, "after": "ru"},
            {"path": ["llm", "mode"], "kind": "added", "before": None, "after": "brief"},
        ],
        "errors": [{"index": 1, "path": ["llm", "language", "code"], "reason": "path_conflict"}],
    },
    description="Поздняя правка видит созданный ранее scalar и отклоняется атомарно",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
    check_result_isolated=True,
)
def task_xla22_update_profile(profile, updates): ...
