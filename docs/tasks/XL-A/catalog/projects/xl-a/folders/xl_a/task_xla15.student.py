"""
XL-A15. ПРАВКИ — показать последствие до применения.

Работаем с безопасной подготовкой и симуляцией игровых действий.
Все данные локальны: функция не обращается к сети, модели или игре.
Аргументы не меняются. Задачи независимы, а GIVEN-помощники можно
вызывать, но нельзя изменять.

Дополнительный договор данных

Состояние и канонические команды:
    state = {"events": [{"id": "e1", "title": "Рейд", "capacity": 2,
                         "members": ["m1"]}], "next_id": 2}
    create = {"tool": "create_event", "args": {"title": "Рейд", "capacity": 2}}
    join = {"tool": "join_event", "args": {"event_id": "e1", "member_id": "m2"}}

next_id задаёт следующий свободный номер eN. create_event добавляет
событие с пустым members, увеличивает next_id и возвращает value={event_id}.
join_event добавляет участника и возвращает value={event_id, member_id}.
Порядок отказов вступления: unknown_event, already_joined, event_full.
Неизвестная команда отклоняется с unknown_tool. given_dispatch возвращает
{status, state, result, reason}: при успехе status="done", result=value,
reason=None; при отказе status="rejected", result=None, reason — код отказа,
state равно исходному состоянию. Входные объекты сохраняются.

Работай с этой функцией. GIVEN-помощники можно вызывать, но нельзя изменять.
"""


# GIVEN: готовый помощник для этой задачи.


def given_create_event(state, args):
    """GIVEN: чисто создать событие и вернуть {ok,state,value,error}."""
    import copy

    new_state = copy.deepcopy(state)
    event_id = f"e{new_state['next_id']}"
    new_state["next_id"] += 1
    new_state["events"].append(
        {"id": event_id, "title": args["title"], "capacity": args["capacity"], "members": []}
    )
    return {"ok": True, "state": new_state, "value": {"event_id": event_id}, "error": None}


# GIVEN: готовый помощник для этой задачи.


def given_join_event(state, args):
    """GIVEN: чисто вступить в событие с фиксированным порядком отказов."""
    import copy

    new_state = copy.deepcopy(state)
    event = next((item for item in new_state["events"] if item["id"] == args["event_id"]), None)
    if event is None:
        return {"ok": False, "state": copy.deepcopy(state), "value": None, "error": "unknown_event"}
    if args["member_id"] in event["members"]:
        return {
            "ok": False,
            "state": copy.deepcopy(state),
            "value": None,
            "error": "already_joined",
        }
    if len(event["members"]) >= event["capacity"]:
        return {"ok": False, "state": copy.deepcopy(state), "value": None, "error": "event_full"}
    event["members"].append(args["member_id"])
    return {
        "ok": True,
        "state": new_state,
        "value": {"event_id": event["id"], "member_id": args["member_id"]},
        "error": None,
    }


# GIVEN: готовый помощник для этой задачи.


def given_dispatch(state, command):
    """
    GIVEN: корректная обычная отправка.
    """
    import copy

    if command["tool"] == "create_event":
        handled = given_create_event(state, command["args"])
    elif command["tool"] == "join_event":
        handled = given_join_event(state, command["args"])
    else:
        return {
            "status": "rejected",
            "state": copy.deepcopy(state),
            "result": None,
            "reason": "unknown_tool",
        }
    if not handled["ok"]:
        return {
            "status": "rejected",
            "state": copy.deepcopy(state),
            "result": None,
            "reason": handled["error"],
        }
    return {"status": "done", "state": handled["state"], "result": handled["value"], "reason": None}


def task_xla15_preview_action(state, command, mode="apply"):
    """
    XL-A15. ПРАВКИ — показать последствие до применения.

    До подтверждения игрок хочет увидеть, что произойдёт с локальным
    состоянием гильдии. Добавь режим preview, сохранив старый режим apply.
    Никаких реальных игровых вызовов здесь нет: это чистая симуляция.

    Аргументы:
        state содержит события и next_id; command — каноническая
        команда create_event или join_event. Форматы приведены в договоре данных. mode гарантированно равен
        'apply' либо 'preview'. Для корректного обычного выполнения вызывай
        given_dispatch, приведённый в этом файле.

    Верни ключи status, state, result, reason, preview_state.
    В apply поведение совпадает с given_dispatch, включая отказ: поле
    preview_state всегда None. В preview при успехе status='preview',
    state равен исходному состоянию, result содержит предсказанный value,
    reason=None, а preview_state содержит предсказанное новое состояние.
    При отказе preview верни status='rejected', исходный state, result=None,
    reason из диспетчера и preview_state=None. Сам исходный state никогда
    не меняется. Предпросмотр создания показывает увеличенный next_id в
    preview_state, но не расходует его в возвращаемом state.

    Пример:
        state={"events":[],"next_id":1}
        command={"tool":"create_event","args":{"title":"Рейд","capacity":4}}
        task_xla15_preview_action(state, command, "preview") == {
            "status":"preview","state":{"events":[],"next_id":1},
            "result":{"event_id":"e1"},"reason":None,
            "preview_state":{"events":[{"id":"e1","title":"Рейд",
            "capacity":4,"members":[]}],"next_id":2}}
    Второй пример: та же команда в apply возвращает
    {"status":"done","state":{"events":[{"id":"e1","title":"Рейд",
    "capacity":4,"members":[]}],"next_id":2},"result":{"event_id":"e1"},
    "reason":None,"preview_state":None}.
    Третий пример: state как выше и join_event с event_id='missing',
    member_id='m1' в preview даёт rejected, исходный state, result=None,
    reason='unknown_event', preview_state=None.

    Сохрани прежний контракт apply для всех корректных и отказных команд.
    Проверь, что повторный вызов preview с тем же входом даёт тот же
    прогноз и не меняет входные словари или списки.
    """
    result = given_dispatch(state, command)
    result["preview_state"] = None
    return result
