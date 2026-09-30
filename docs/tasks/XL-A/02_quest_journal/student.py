"""
XL-A / 02. Квестовый журнал — XL-A04, XL-A05, XL-A06.

Все ID и названия — строки. Числа — целые. Входные объекты менять нельзя.
Каждая задача самостоятельна и содержит собственный договор данных.
В баговой задаче сдай исправление, причину и воспроизводящий пример.
В задаче на правки проверь старый простой случай и новые требования.
"""

from copy import deepcopy


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


def task_xla05_claim_reward(player, quest_id, rewards):
    """
    XL-A05. НАЙТИ БАГ — награда выдаётся повторно.

    Игрок дважды нажал «Забрать». Исправь код, чтобы один квест
    приносил награду только один раз, включая последовательные вызовы.

    Вход:
        player = {"gold": 10, "completed": ["q1"], "claimed": []}.
        rewards = {"q1": 5, "q2": 20}; значения — золото >= 0.
        completed и claimed — списки уникальных ID; claimed входит в completed.

    Результат: {"status": строка, "player": новое состояние}.
    Проверки строго в таком порядке:
        1. quest_id нет в rewards -> "unknown_quest".
        2. Награда уже в claimed -> "already_claimed".
        3. quest_id нет в completed -> "not_completed".
        4. Иначе -> "claimed": прибавить золото, дописать ID в конец claimed.
    completed не меняется. При любом отказе состояние равно исходному.
    Входной player, в том числе его списки, изменять нельзя.

    Пример:
        first = task_xla05_claim_reward(
            {"gold": 10, "completed": ["q1"], "claimed": []}, "q1", {"q1": 5})
        Ожидаем:
            {"status": "claimed", "player":
             {"gold": 15, "completed": ["q1"], "claimed": ["q1"]}}.
        Второй вызов с first["player"] -> status="already_claimed",
        gold остаётся 15, claimed остаётся ["q1"].
        Запрос неизвестного q9 -> unknown_quest, всё состояние прежнее.

        assert task_xla05_claim_reward(first["player"], "q1", {"q1": 5}) == {
            "status": "already_claimed", "player": first["player"]}
        assert task_xla05_claim_reward(first["player"], "q9", {"q1": 5}) == {
            "status": "unknown_quest", "player": first["player"]}

    Проверь также нулевую награду и известный, но незавершённый квест.
    Пример повторного вызова должен входить в твою проверку исправления.
    """
    result = deepcopy(player)
    if quest_id not in rewards:
        return {"status": "unknown_quest", "player": result}
    if quest_id not in player["completed"]:
        return {"status": "not_completed", "player": result}
    result["gold"] += rewards[quest_id]
    result["claimed"].append(quest_id)
    return {"status": "claimed", "player": result}


def task_xla06_advance_quest(quest, events):
    """
    XL-A06. ПРАВКИ — квест с несколькими целями.

    Сейчас обработчик поддерживает одну цель. Расширь его для квеста
    «победи волков И собери травы», сохранив старый случай одной цели.

    Вход:
        quest = {"id": "q1", "objectives": [
            {"id": "wolves", "target": 3, "progress": 1},
            {"id": "herbs", "target": 5, "progress": 0}] }.
        У целей уникальные id, target > 0, 0 <= progress <= target.
        events = [{"objective_id": "wolves", "amount": 2}, ...].
        amount >= 0. События могут повторяться и ссылаться на неизвестную цель.

    Правила:
        Обрабатывать события по порядку. Известной цели прибавить amount,
        ограничив progress её target. Остальные цели не трогать.
        Неизвестную цель пропустить, добавить индекс события в rejected.
        completed=True, только если достигнуты ВСЕ цели.
        Квест без целей считается завершённым; все его события неизвестны.
        Порядок целей и дополнительные поля quest сохранить.

    Верни:
        {"quest": новое состояние, "completed": bool, "rejected": [индексы]}.

    Пример для quest выше:
        events = [{"objective_id": "wolves", "amount": 10},
                  {"objective_id": "ghost", "amount": 1},
                  {"objective_id": "herbs", "amount": 4}]
        -> progress: wolves=3, herbs=4; completed=False; rejected=[1].
        Ещё одно событие herbs с amount=1 на обновлённом квесте
        -> wolves=3, herbs=5; completed=True; rejected=[].
        events=[] -> неизменный квест и completed по его текущим целям.

        single = {"id": "q", "objectives": [
            {"id": "herbs", "target": 2, "progress": 1}]}
        assert task_xla06_advance_quest(single, [
            {"objective_id": "herbs", "amount": 3}]) == {
            "quest": {"id": "q", "objectives": [
                {"id": "herbs", "target": 2, "progress": 2}]},
            "completed": True, "rejected": []}
        assert task_xla06_advance_quest(single, []) == {
            "quest": single, "completed": False, "rejected": []}

    Проверь: одну цель; несколько событий одной цели; превышение target;
    завершённый квест; отсутствие изменений в исходном quest.
    """
    updated = deepcopy(quest)
    rejected = []
    first = updated["objectives"][0] if updated["objectives"] else None
    for index, event in enumerate(events):
        if first is None or event["objective_id"] != first["id"]:
            rejected.append(index)
            continue
        first["progress"] = min(first["target"], first["progress"] + event["amount"])
    completed = first is None or first["progress"] == first["target"]
    return {"quest": updated, "completed": completed, "rejected": rejected}
