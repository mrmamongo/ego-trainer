"""
XL-A / 03. Поиск группы в MMO — XL-A07, XL-A08, XL-A09.

Роли: tank, healer, damage. У игрока ровно одна роль.
Все количества, уровни и время ожидания — целые числа не меньше нуля.
Чем больше wait_seconds, тем дольше игрок ждёт группу.
Входные данные менять нельзя. Задачи независимы друг от друга.
В задаче с ошибкой подготовь объяснение и пример, где она воспроизводится.
"""


def task_xla07_find_candidates(players, min_level, role=None, language=None):
    """
        XL-A07. ПРАВКИ — найти тех, с кем получится играть.

        Поиск уже умеет учитывать онлайн, уровень и роль. Добавь фильтр языка
        общения: играть должны те, кто говорит на нужном языке. Язык сравнивается
        точным совпадением кода, например "ru".

        Что приходит на вход:
            players — записи с уникальными id:
                {"id": "A", "level": 12, "role": "tank",
                 "languages": ["ru", "en"], "online": True}.
            min_level — минимальный уровень, он допустим (включительно).
            role — требуемая роль или None (любая).
            language — код языка или None (любой).

        Верни список ID в ИСХОДНОМ порядке players.
        Игрок должен быть online, иметь level >= min_level и подходить под оба
        заданных фильтра. Пустой languages не подходит ни под один конкретный
        language, но при language=None он допустим.
        Неизвестный код языка просто не найдёт совпадений.

        Пример:
            players = [
                {"id": "A", "level": 12, "role": "tank", "languages": ["en"], "online": True},
                {"id": "B", "level": 15, "role": "tank", "languages": ["ru", "en"], "online": True},
                {"id": "C", "level": 20, "role": "healer", "languages": ["ru"], "online": False}]
            min_level=12, role="tank", language="ru" -> ["B"].
            min_level=12, role="tank", language=None -> ["A", "B"].
            players=[] -> [].

            assert task_xla07_find_candidates(players, 12, "tank", "ru") == ["B"]
            assert task_xla07_find_candidates(players, 12, "tank") == ["A", "B"]

        Что должно остаться как раньше: вызовы со старым набором аргументов
        должны возвращать прежний ответ. Новый фильтр не должен обходить
        проверку online/level.
        """
    found = []
    for player in players:
        if not player["online"] or player["level"] < min_level:
            continue
        if role is not None and player["role"] != role:
            continue
        found.append(player["id"])
    return found


# GIVEN: порядок кандидатов внутри роли.
def given_order_candidates(players):
    return sorted(players, key=lambda player: (-player["wait_seconds"], player["id"]))


def task_xla08_build_party(players, slots):
    """
        XL-A08. НОВЫЙ КОД — собрать пати по заявкам.

        Заявки уже отфильтрованы. Теперь нужно заполнить места в группе
        по ролям. В этой задаче ID игроков уникальны; смены и совмещения ролей
        нет.

        Что приходит на вход:
            players = [{"id": "A", "role": "tank", "wait_seconds": 30}, ...].
            slots = {"tank": 1, "healer": 1, "damage": 2}.
            В slots могут отсутствовать роли: для них требуется 0 мест.

        Правила:
            Роли заполняются в порядке tank, healer, damage.
            Внутри роли раньше берём того, кто дольше ждёт.
            При одинаковом ожидании — меньший по алфавиту id.
            Можно использовать given_order_candidates.
            В members сначала танки, затем лекари, затем бойцы.
            Если игроков не хватает, верни частичный состав — не обнуляй его.

        Результат:
            {"members": [ID],
             "missing": {"tank": int, "healer": int, "damage": int},
             "ready": bool}.
            Все роли в missing обязательны, даже с нулевым значением.
            ready=True, когда не осталось незаполненных мест. Для slots={} это True.

        Пример:
            players = [{"id": "T", "role": "tank", "wait_seconds": 10},
                       {"id": "B", "role": "damage", "wait_seconds": 20},
                       {"id": "A", "role": "damage", "wait_seconds": 20}]
            slots={"tank": 1, "healer": 1, "damage": 1}
            -> {"members": ["T", "A"],
                "missing": {"tank": 0, "healer": 1, "damage": 0}, "ready": False}.
            slots={} -> members=[], все missing=0, ready=True.

            assert task_xla08_build_party(players, {"tank": 1, "healer": 1, "damage": 1}) == {
                "members": ["T", "A"],
                "missing": {"tank": 0, "healer": 1, "damage": 0}, "ready": False}
            assert task_xla08_build_party([], {}) == {
                "members": [],
                "missing": {"tank": 0, "healer": 0, "damage": 0}, "ready": True}

        Проверь равное ожидание, лишних кандидатов, нулевые места и пустую очередь.
        """
    pass


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
