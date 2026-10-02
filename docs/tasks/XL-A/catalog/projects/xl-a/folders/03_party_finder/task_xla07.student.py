"""
XL-A07. ПРАВКИ — найти тех, с кем получится играть.

Роли: tank, healer, damage. У игрока ровно одна роль.
Все количества, уровни и время ожидания — целые >= 0.
Чем больше wait_seconds, тем дольше игрок ждёт.
Входные данные менять нельзя. Задачи независимы.
Для бага подготовь объяснение и воспроизводящий пример.

Работай с этой функцией. GIVEN-помощники можно вызывать, но нельзя изменять.
"""


def task_xla07_find_candidates(players, min_level, role=None, language=None):
    """
    XL-A07. ПРАВКИ — найти тех, с кем получится играть.

    Поиск уже умеет учитывать онлайн, уровень и роль. Добавь фильтр
    языка общения. Это точное совпадение кода языка, например "ru".

    Вход:
        players — записи с уникальными id:
            {"id": "A", "level": 12, "role": "tank",
             "languages": ["ru", "en"], "online": True}.
        min_level — минимальный уровень включительно.
        role — требуемая роль или None (любая).
        language — код языка или None (любой).

    Верни список ID в ИСХОДНОМ порядке players.
    Игрок должен быть online, иметь level >= min_level и подходить
    под оба заданных фильтра. Пустой languages не подходит ни под один
    конкретный language, но допустим при language=None.
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

    Совместимость: вызовы со старым набором аргументов должны возвращать
    прежний ответ. Новый фильтр не должен обходить проверку online/level.
    """
    found = []
    for player in players:
        if not player["online"] or player["level"] < min_level:
            continue
        if role is not None and player["role"] != role:
            continue
        found.append(player["id"])
    return found
