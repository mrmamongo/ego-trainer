"""
XL-A14. НАЙТИ БАГ — отказное действие выглядит успешным.

Здесь мы безопасно готовим и проигрываем игровые действия: сначала
проверяем, что игрок имел в виду, а потом показываем (или применяем)
результат — без риска что-то сломать в игре.
Все данные локальные: функция не обращается к сети, модели или самой игре.
Аргументы не меняются. Задачи независимы друг от друга, а готовые
функции (GIVEN) можно вызывать, но нельзя изменять.

Работай с этой функцией. GIVEN-помощники можно вызывать, но нельзя изменять.
"""


# GIVEN: готовый помощник для этой задачи.


def given_create_event(state, args):
    """GIVEN: создать событие, не меняя вход; вернуть {ok,state,value,error}."""
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
    """GIVEN: вступить в событие, не меняя вход; отказы идут в фиксированном порядке."""
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


def task_xla14_dispatch(state, command):
    """
        XL-A14. НАЙТИ БАГ — отказное действие выглядит успешным.

        Симулятор событий гильдии уже умеет создавать событие и добавлять
        участника. Обёртка над ним должна различать успешный результат и штатный
        отказ обработчика, но сейчас интерфейс может сообщить «готово», хотя
        участник на самом деле не добавлен. Исправь функцию, сохранив её
        сигнатуру и формат ответа.

        Аргументы:
            state={events:[{id,title,capacity,members:[ID]}], next_id:int}.
            command — обычная команда: create_event с args {title,capacity}
            или join_event с args {event_id,member_id}. next_id задаёт следующий
            свободный номер eN. Используй подходящий GIVEN-обработчик.

        Результат всегда содержит status, state, result, reason. При успехе
        status='done', state — состояние обработчика, result — его value,
        reason=None. При отказе status='rejected', state остаётся равным
        исходному состоянию, result=None, reason — код отказа обработчика.
        Неизвестный tool отклоняется с reason='unknown_tool'. Для join причины
        проверяются обработчиком в порядке unknown_event, already_joined,
        event_full. Успешное вступление добавляет member_id, а создание выдаёт
        event_id. Входные объекты не меняй.

        Пример:
            state={"events":[{"id":"e1","title":"Рейд","capacity":1,
                               "members":["m1"]}],"next_id":2}
            command={"tool":"join_event","args":{"event_id":"e1","member_id":"m2"}}
            task_xla14_dispatch(state, command) == {
                "status":"rejected","state":state,"result":None,"reason":"event_full"}
        Второй пример: state={"events":[{"id":"e1","title":"Рейд",
        "capacity":2,"members":[]}],"next_id":2}, та же команда для m2 даёт
        {"status":"done","state":{"events":[{"id":"e1","title":"Рейд",
        "capacity":2,"members":["m2"]}],"next_id":2},
        "result":{"event_id":"e1","member_id":"m2"},"reason":None}.

        Проверь также неизвестное событие, повторное вступление и неизвестный
        tool. В сдаче укажи причину бага и пример, на котором старый и новый
        результат различаются. Всё это только симуляция, внешних действий нет.
        """
    if command["tool"] == "create_event":
        handled = given_create_event(state, command["args"])
    elif command["tool"] == "join_event":
        handled = given_join_event(state, command["args"])
    else:
        return {"status": "rejected", "state": state, "result": None, "reason": "unknown_tool"}
    if handled:
        return {
            "status": "done",
            "state": handled["state"],
            "result": handled["value"],
            "reason": None,
        }
    return {"status": "rejected", "state": state, "result": None, "reason": handled["error"]}
