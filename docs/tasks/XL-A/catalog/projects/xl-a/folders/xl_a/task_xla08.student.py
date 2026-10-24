"""
XL-A08. НОВЫЙ КОД — собрать пати по заявкам.

Роли: tank, healer, damage. У игрока ровно одна роль.
Все количества, уровни и время ожидания — целые числа не меньше нуля.
Чем больше wait_seconds, тем дольше игрок ждёт группу.
Входные данные менять нельзя. Задачи независимы друг от друга.
В задаче с ошибкой подготовь объяснение и пример, где она воспроизводится.

Работай с этой функцией. GIVEN-помощники можно вызывать, но нельзя изменять.
"""


# GIVEN: готовый помощник для этой задачи.


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
