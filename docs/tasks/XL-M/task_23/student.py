"""XL-M-23 — Исправь трекинг квестов (баг: прогресс).

Квест имеет objectives: [{"id": ...,
"type": "kill|collect|talk",
"target": str, "count": N}].
Игрок совершает действия —
progress_quest(quest, action):
action {"type": ..., "target": ...,
"value": N}. Нужно увеличить
progress соответствующего objective
на value, но не сверх count.

Текущая версия обнуляет
progress каждый раз вместо
прибавления. Исправь.

Если все objectives выполнены
(count >= target) — верни
{"quest_done": True}, иначе
{"quest_done": False}.

Пример:
    q = {"objectives": [{"id":"o1","type":"kill","target":"rat","count":5,"progress":0}]}
    progress_quest(q, {"type":"kill","target":"rat","value":3})
    → {"quest_done": False}
    progress_quest(q, {"type":"kill","target":"rat","value":2})
    → {"quest_done": True}
"""


def progress_quest(quest, action):
    for obj in quest["objectives"]:
        if obj["type"] == action["type"] and obj["target"] == action["target"]:
            obj["progress"] = action["value"]  # баг: обнуляет
    done = all(
        o["progress"] >= o["count"] for o in quest["objectives"]
    )
    return {"quest_done": done}


if __name__ == "__main__":
    q = {
        "objectives": [
            {"id": "o1", "type": "kill", "target": "rat", "count": 5, "progress": 0}
        ]
    }
    print(progress_quest(q, {"type": "kill", "target": "rat", "value": 3}))
    print(progress_quest(q, {"type": "kill", "target": "rat", "value": 2}))
