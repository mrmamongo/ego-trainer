"""
XL-A06. ПРАВКИ — квест с несколькими целями.

Все ID и названия — строки. Числа — целые. Входные объекты менять нельзя.
Каждая задача самостоятельна и содержит собственный договор данных.
В баговой задаче сдай исправление, причину и воспроизводящий пример.
В задаче на правки проверь старый простой случай и новые требования.

Работай с этой функцией. GIVEN-помощники можно вызывать, но нельзя изменять.
"""


from copy import deepcopy


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
