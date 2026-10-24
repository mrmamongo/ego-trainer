"""
XL-A09. НАЙТИ БАГ — один игрок занимает два места.

Роли: tank, healer, damage. У игрока ровно одна роль.
Все количества, уровни и время ожидания — целые >= 0.
Чем больше wait_seconds, тем дольше игрок ждёт.
Входные данные менять нельзя. Задачи независимы.
Для бага подготовь объяснение и воспроизводящий пример.

Дополнительный договор данных

Места и результат подбора:
    slots = {"tank": 1, "healer": 1, "damage": 2}
    result = {"members": [ID],
              "missing": {"tank": int, "healer": int, "damage": int},
              "ready": bool}

Количество мест — целое >= 0. Отсутствующая в slots роль требует 0 мест.
Роли обрабатываются в порядке tank, healer, damage. Внутри роли сначала
выбирается большее wait_seconds, при равенстве — меньший по алфавиту ID
игрока. members следует этому порядку. При нехватке сохраняется частичный
состав. В missing всегда все три роли и число незаполненных мест каждой.
ready=True ровно при отсутствии незаполненных мест. Для slots={}
members=[], все значения missing равны 0, ready=True.

Работай с этой функцией. GIVEN-помощники можно вызывать, но нельзя изменять.
"""


# GIVEN: готовый помощник для этой задачи.


def given_order_candidates(players):
    return sorted(players, key=lambda player: (-player["wait_seconds"], player["id"]))


def task_xla09_party_from_tickets(tickets, slots):
    """
    XL-A09. НАЙТИ БАГ — один игрок занимает два места.

    Пользователь несколько раз нажал поиск, и сервис создал разные заявки
    на одного игрока. Исправь подборщик: повторная заявка не даёт нового места.

    Вход:
        tickets = [{"ticket_id": "r1", "player_id": "A",
                    "role": "tank", "wait_seconds": 30}, ...].
        ticket_id уникальны. У заявок одного player_id одинаковые role
        и wait_seconds. Форматы slots и результата приведены в договоре данных этой задачи.

    Правила:
        Каждый player_id участвует в отборе один раз.
        Приоритет определяется wait_seconds, затем player_id, а не ticket_id.
        Порядок ролей: tank, healer, damage. Вернуть частичный состав,
        если уникальных игроков не хватает.

    Пример:
        tickets = [{"ticket_id": "r1", "player_id": "A", "role": "tank", "wait_seconds": 30},
                   {"ticket_id": "r2", "player_id": "A", "role": "tank", "wait_seconds": 30}]
        slots={"tank": 2} ->
            {"members": ["A"],
             "missing": {"tank": 1, "healer": 0, "damage": 0}, "ready": False}.
        Если добавить B/tank/wait_seconds=20, состав станет ["A", "B"].

        assert task_xla09_party_from_tickets(tickets, {"tank": 2}) == {
            "members": ["A"],
            "missing": {"tank": 1, "healer": 0, "damage": 0}, "ready": False}
        assert task_xla09_party_from_tickets(tickets, {}) == {
            "members": [],
            "missing": {"tank": 0, "healer": 0, "damage": 0}, "ready": True}

    Проверь дубликаты не рядом, три заявки одного игрока и очередь без
    повторов. Перестановка одинаковых по смыслу заявок не меняет ответ.
    Объясни, что именно в предметной области должно быть уникальным.
    """
    seen = set()
    candidates = []
    for ticket in tickets:
        if ticket["ticket_id"] in seen:
            continue
        seen.add(ticket["ticket_id"])
        candidates.append(
            {
                "id": ticket["player_id"],
                "role": ticket["role"],
                "wait_seconds": ticket["wait_seconds"],
            }
        )
    candidates = given_order_candidates(candidates)
    members = []
    missing = {}
    for role in ("tank", "healer", "damage"):
        matching = [p for p in candidates if p["role"] == role]
        selected = matching[: slots.get(role, 0)]
        members.extend(p["id"] for p in selected)
        missing[role] = slots.get(role, 0) - len(selected)
    return {
        "members": members,
        "missing": missing,
        "ready": all(value == 0 for value in missing.values()),
    }
