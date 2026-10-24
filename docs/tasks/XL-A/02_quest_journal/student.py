"""
XL-A / 02. Квестовый журнал — XL-A04, XL-A05, XL-A06.

Все ID и названия — строки, числа — целые. Входные объекты менять нельзя.
Каждая задача самостоятельна: всё, что нужно для решения, есть в её условии.
В задаче с ошибкой сдай исправление, объяснение причины
и пример, на котором ошибка воспроизводится.
В задаче на доработку проверь и старый простой случай, и новые требования.
"""

from copy import deepcopy


def task_xla04_quest_journal(catalog, progress, player_level, zone):
    """
        XL-A04. НОВЫЙ КОД — показать игроку его квесты.

        Журнал квестов в игре показывает три вкладки: что доступно, что уже
        начато и что завершено. Каталог знает, какие квесты существуют, а
        сохранение — какие из них игрок начал. Собери данные для этих трёх
        вкладок.

        Что приходит на вход:
            catalog — список квестов с уникальными id:
                {"id": "q1", "title": "Травы", "min_level": 2, "zone": "forest"}.
            progress — {quest_id: "active" или "completed"}.
            player_level — уровень игрока (не меньше нуля); zone — зона,
                которую он выбрал.

        Правила:
            Смотрим только квесты выбранной зоны.
            Известный progress="active" -> вкладка active.
            progress="completed" -> completed.
            Начатые и завершённые видны независимо от текущего уровня игрока.
            Квест без progress доступен, если player_level >= min_level.
            Остальные квесты скрыты. ID из progress, которых нет в каталоге,
            игнорируем.
            Внутри каждой вкладки порядок такой: сначала min_level по возрастанию,
            затем id по алфавиту. title на порядок не влияет.

        Верни только ID:
            {"available": [...], "active": [...], "completed": [...]}.
            Все три ключа должны быть даже тогда, когда результат пустой.

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

        Проверь ещё: одинаковые min_level, неизвестную зону и завершённый квест,
        у которого min_level выше уровня игрока. Никакие статусы менять не нужно.
        """
    pass


def task_xla05_claim_reward(player, quest_id, rewards):
    """
        XL-A05. НАЙТИ БАГ — награда выдаётся повторно.

        Игрок дважды нажал «Забрать», и награда за квест пришла два раза.
        Исправь код так, чтобы один квест приносил награду только один раз,
        в том числе при последовательных вызовах функции.

        Что приходит на вход:
            player = {"gold": 10, "completed": ["q1"], "claimed": []}.
            rewards = {"q1": 5, "q2": 20}; значения — золото >= 0.
            completed и claimed — списки уникальных ID; claimed входит в completed.

        Верни: {"status": строка, "player": новое состояние}.
        Проверки идут строго в таком порядке:
            1. quest_id нет в rewards -> "unknown_quest".
            2. Награда уже в claimed -> "already_claimed".
            3. quest_id нет в completed -> "not_completed".
            4. Иначе -> "claimed": прибавить золото, дописать ID в конец claimed.
        completed не меняется. При любом отказе состояние равно исходному.
        Входной player менять нельзя — в том числе его списки.

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
        Пример с повторным вызовом должен быть в твоей проверке исправления.
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

        Сейчас обработчик умеет вести одну цель квеста. Расширь его для квестов
        вида «победи волков И собери травы», сохранив прежнее поведение для
        квеста с одной целью.

        Что приходит на вход:
            quest = {"id": "q1", "objectives": [
                {"id": "wolves", "target": 3, "progress": 1},
                {"id": "herbs", "target": 5, "progress": 0}] }.
            У целей уникальные id, target > 0, 0 <= progress <= target.
            events = [{"objective_id": "wolves", "amount": 2}, ...].
            amount >= 0. События могут повторяться и ссылаться на неизвестную цель.

        Правила:
            Обрабатывай события по порядку. Известной цели прибавь amount,
            но progress не должен уйти выше её target. Остальные цели не трогай.
            Неизвестную цель пропусти и добавь индекс события в rejected.
            completed=True только тогда, когда достигнуты ВСЕ цели.
            Квест без целей считается завершённым; все его события неизвестны.
            Порядок целей и дополнительные поля quest сохрани.

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
        завершённый квест; то, что исходный quest остался прежним.
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
