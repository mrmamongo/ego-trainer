"""
XL-A09. НАЙТИ БАГ — один игрок занимает два места.

Роли: tank, healer, damage. У игрока ровно одна роль.
Все количества, уровни и время ожидания — целые числа не меньше нуля.
Чем больше wait_seconds, тем дольше игрок ждёт группу.
Входные данные менять нельзя. Задачи независимы друг от друга.
В задаче с ошибкой подготовь объяснение и пример, где она воспроизводится.

Дополнительный договор данных


    Как выглядит подбор группы:
        slots = {"tank": 1, "healer": 1, "damage": 2}
        result = {"members": [ID],
                  "missing": {"tank": int, "healer": int, "damage": int},
                  "ready": bool}

    Количество мест — целое число не меньше нуля. Если роли нет в slots,
    для неё нужно 0 мест.
    Роли обрабатываются в порядке tank, healer, damage. Внутри роли сначала
    выбирается тот, кто дольше ждёт (больше wait_seconds), а при равенстве —
    меньший по алфавиту ID игрока. members идут в этом же порядке. Если
    игроков не хватает, сохраняется частичный состав. В missing всегда есть
    все три роли и число незаполненных мест каждой.
    ready=True ровно тогда, когда незаполненных мест нет. Для slots={}
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
        на одного игрока. Исправь подборщик: повторная заявка не должна давать
        игроку ещё одно место.

        Что приходит на вход:
            tickets = [{"ticket_id": "r1", "player_id": "A",
                        "role": "tank", "wait_seconds": 30}, ...].
            ticket_id уникальны. У заявок одного player_id одинаковые role
            и wait_seconds. Правила для slots и результата — в дополнительных
            правилах данных этой задачи.

        Правила:
            Каждый player_id участвует в отборе один раз.
            Приоритет определяется wait_seconds, затем player_id, а не ticket_id.
            Порядок ролей: tank, healer, damage. Если уникальных игроков не
            хватает, верни частичный состав.

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

        Проверь дубликаты, стоящие не рядом, три заявки одного игрока и
        очередь без повторов. Перестановка одинаковых по смыслу заявок не
        должна менять ответ. В объяснении напиши, что именно в этой предметной
        области обязательно должно быть уникальным.
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
