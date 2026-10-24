"""
XL-A04. НОВЫЙ КОД — показать игроку его квесты.

Все ID и названия — строки. Числа — целые. Входные объекты менять нельзя.
Каждая задача самостоятельна и содержит собственный договор данных.
В баговой задаче сдай исправление, причину и воспроизводящий пример.
В задаче на правки проверь старый простой случай и новые требования.

Работай с этой функцией. GIVEN-помощники можно вызывать, но нельзя изменять.
"""


def task_xla04_quest_journal(catalog, progress, player_level, zone):
    """
    XL-A04. НОВЫЙ КОД — показать игроку его квесты.

    Каталог знает, какие квесты существуют, а сохранение — какие начаты.
    Собери данные для трёх вкладок журнала.

    Вход:
        catalog — список с уникальными id:
            {"id": "q1", "title": "Травы", "min_level": 2, "zone": "forest"}.
        progress — {quest_id: "active" или "completed"}.
        player_level — уровень >= 0; zone — выбранная зона.

    Правила:
        Рассматриваем только квесты выбранной зоны.
        Известный progress="active" -> вкладка active.
        progress="completed" -> completed.
        Начатые и завершённые видны независимо от текущего уровня игрока.
        Квест без progress доступен, если player_level >= min_level.
        Остальные квесты скрыты. Неизвестные каталогу ID из progress игнорируем.
        Внутри каждой вкладки порядок: min_level по возрастанию,
        затем id по алфавиту. title на порядок не влияет.

    Верни только ID:
        {"available": [...], "active": [...], "completed": [...]}.
        Все три ключа должны быть даже при пустом результате.

    Пример:
        catalog = [
            {"id": "q2", "title": "Волки", "min_level": 5, "zone": "forest"},
            {"id": "q1", "title": "Травы", "min_level": 2, "zone": "forest"},
            {"id": "q3", "title": "Рыба", "min_level": 1, "zone": "lake"}]
        progress = {"q2": "active", "unknown": "completed"}
        player_level=2, zone="forest" ->
            {"available": ["q1"], "active": ["q2"], "completed": []}.
        С теми же данными и player_level=1 available станет [].
        Пустой catalog -> все три списка пустые.

        assert task_xla04_quest_journal(catalog, progress, 2, "forest") == {
            "available": ["q1"], "active": ["q2"], "completed": []}
        assert task_xla04_quest_journal([], {}, 2, "forest") == {
            "available": [], "active": [], "completed": []}

    Проверь равные min_level, неизвестную зону и завершённый квест
    с min_level выше уровня игрока. Никакие статусы изменять не нужно.
    """
    pass
