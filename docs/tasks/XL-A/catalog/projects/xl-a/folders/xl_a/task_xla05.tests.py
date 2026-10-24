from ego.testing import case


@case(
    args=({"gold": 10, "completed": ["q1"], "claimed": []}, "q1", {"q1": 5}),
    expected={
        "status": "claimed",
        "player": {
            "gold": 15,
            "completed": ["q1"],
            "claimed": ["q1"],
        },
    },
    description="Первая выдача добавляет золото и помечает награду полученной",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=({"gold": 15, "completed": ["q1"], "claimed": ["q1"]}, "q1", {"q1": 5}),
    expected={
        "status": "already_claimed",
        "player": {
            "gold": 15,
            "completed": ["q1"],
            "claimed": ["q1"],
        },
    },
    description="Повторный вызов с состоянием после первой выдачи не даёт награду снова",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=({"gold": 10, "completed": ["q1"], "claimed": []}, "q2", {"q1": 5, "q2": 20}),
    expected={
        "status": "not_completed",
        "player": {
            "gold": 10,
            "completed": ["q1"],
            "claimed": [],
        },
    },
    description="Известный незавершённый квест не приносит золота",
    level="smoke",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=({"gold": 50, "completed": ["ghost"], "claimed": ["ghost"]}, "ghost", {"q1": 5}),
    expected={
        "status": "unknown_quest",
        "player": {
            "gold": 50,
            "completed": ["ghost"],
            "claimed": ["ghost"],
        },
    },
    description="Неизвестный rewards квест проверяется раньше already_claimed",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=({"gold": 10, "completed": ["q1"], "claimed": []}, "q9", {"q1": 5}),
    expected={
        "status": "unknown_quest",
        "player": {
            "gold": 10,
            "completed": ["q1"],
            "claimed": [],
        },
    },
    description="Неизвестный квест проверяется раньше завершённости",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=({"gold": 0, "completed": ["q0"], "claimed": []}, "q0", {"q0": 0}),
    expected={
        "status": "claimed",
        "player": {
            "gold": 0,
            "completed": ["q0"],
            "claimed": ["q0"],
        },
    },
    description="Нулевая награда тоже записывается в claimed",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=({"gold": 0, "completed": ["q0"], "claimed": ["q0"]}, "q0", {"q0": 0}),
    expected={
        "status": "already_claimed",
        "player": {
            "gold": 0,
            "completed": ["q0"],
            "claimed": ["q0"],
        },
    },
    description="Повторная выдача нулевой награды также отклоняется",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=({"gold": 7, "completed": ["b", "z", "a"], "claimed": ["z"]}, "b", {"b": 3, "z": 7}),
    expected={
        "status": "claimed",
        "player": {
            "gold": 10,
            "completed": ["b", "z", "a"],
            "claimed": ["z", "b"],
        },
    },
    description="ID дописывается в конец claimed, порядок completed сохраняется",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=({"gold": 15, "completed": ["q1", "q2"], "claimed": ["q1"]}, "q2", {"q1": 5, "q2": 20}),
    expected={
        "status": "claimed",
        "player": {
            "gold": 35,
            "completed": ["q1", "q2"],
            "claimed": ["q1", "q2"],
        },
    },
    description="После первой награды можно получить другую завершённую награду",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=({"gold": 0, "completed": [], "claimed": []}, "q1", {}),
    expected={
        "status": "unknown_quest",
        "player": {
            "gold": 0,
            "completed": [],
            "claimed": [],
        },
    },
    description="Пустой справочник наград и пустые списки игрока",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
@case(
    args=(
        {"gold": 35, "completed": ["q1", "q2"], "claimed": ["q1", "q2"]},
        "q1",
        {"q1": 100, "q2": 20},
    ),
    expected={
        "status": "already_claimed",
        "player": {
            "gold": 35,
            "completed": ["q1", "q2"],
            "claimed": ["q1", "q2"],
        },
    },
    description="После нескольких выдач изменение стоимости не разрешает повтор",
    level="full",
    comparison="value",
    check_inputs_unchanged=True,
)
def task_xla05_claim_reward(player, quest_id, rewards): ...
