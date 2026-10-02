"""XL-A / 05. Помощник гильдии — задачи XL-A13, XL-A14, XL-A15.

Работаем с безопасной подготовкой и симуляцией игровых действий.
Все данные локальны: функция не обращается к сети, модели или игре.
Аргументы не меняются. Задачи независимы, а GIVEN-помощники можно
вызывать, но нельзя изменять.
"""


def given_find_matches(items, field, value):
    """GIVEN: найти все записи с точным совпадением значения поля."""
    return [item for item in items if item[field] == value]


def task_xla13_prepare_action(raw, members, events):
    """
    XL-A13. НОВЫЙ КОД — проверить намерение и подготовить команду.

    Модельный вывод уже разобран в словарь, но его нельзя сразу выполнять:
    игрок мог назвать отсутствующего участника или событие. Проверь данные
    и преобразуй названия в канонические ID. Здесь нет реального вызова игры.

    Аргументы:
        raw={tool: строка, args: словарь}.
        Допустимы create_event с title и capacity; join_event с member_name
        и event_title. members=[{id,name}], events=[{id,title,capacity,
        members:[member ID]}]. ID уникальны, имена — нет. Сравнение точное.
        Названия из raw сначала strip(); регистр не меняй. Для имени или
        названия события отсутствующее поле, None, значение не-строка или
        пустая после strip() строка считаются *_empty. Записи каталога
        гарантированно имеют строковые name/title и ID; у событий capacity
        — целое >= 1, members — список ID.

    Всегда верни {status:'ready' или 'rejected', command:..., errors:[...]}.
    Для create_event сначала проверь title: пустая после strip() строка
    даёт title_empty. Затем capacity: нужен int >= 1, bool не считается
    целым; иначе invalid_capacity. Готовая команда содержит tool и args
    с очищенным title и прежним capacity.
    Если неверны оба поля, верни обе ошибки в указанном порядке.
    Отсутствующий или нестроковый title тоже даёт title_empty.
    Лишние поля args игнорируй: в готовую команду входят только описанные поля.
    Для join_event сначала проверь участника, затем событие и собери обе
    независимые ошибки поиска, если они есть. Пустые поля дают
    member_name_empty / event_title_empty. Ноль совпадений —
    unknown_member / unknown_event; больше одного — ambiguous_member /
    ambiguous_event. При уникальных совпадениях проверь уже вступил ли
    участник (already_joined), затем заполненность (event_full).
    Готовые args — только member_id и event_id. Ошибки возвращай в этом
    порядке; при отказе command=None. Неизвестный tool даёт ['unknown_tool'].

    Примеры:
        members=[{"id":"m1","name":"Ира"}]; events=[]
        raw={"tool":"create_event","args":{"title":"  Рейд  ","capacity":4}}
        task_xla13_prepare_action(raw, members, events) == {
            "status":"ready","command":{"tool":"create_event",
            "args":{"title":"Рейд","capacity":4}},"errors":[]}
    Второй пример: members=[{"id":"m1","name":"Ира"},
    {"id":"m2","name":"Ира"}], events=[] и raw=
    {"tool":"join_event","args":{"member_name":"Ира","event_title":"Луна"}}
    дают {"status":"rejected","command":None,
    "errors":["ambiguous_member","unknown_event"]}.
    Третий пример: members=[{"id":"m1","name":"Ира"}], events=[
    {"id":"e1","title":"Рейд","capacity":1,"members":["m2"]}];
    join Ира в Рейд даёт rejected, command=None, errors=['event_full'].
    Если участник уже в заполненном событии, ошибка только already_joined.
    Используй given_find_matches для поиска. Входные данные не меняй.
    """
    pass


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


def task_xla14_dispatch(state, command):
    """
    XL-A14. НАЙТИ БАГ — отказное действие выглядит успешным.

    Симулятор событий уже умеет создавать событие и добавлять участника.
    Обёртка должна различать успешный результат и штатный отказ обработчика.
    Сейчас интерфейс может сообщить «готово», хотя участник не добавлен.
    Исправь функцию, сохранив её сигнатуру и формат ответа.

    Аргументы:
        state={events:[{id,title,capacity,members:[ID]}], next_id:int}.
        command — каноническая команда: create_event с args {title,capacity}
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
    tool. В сдаче укажи причину бага и пример, различающий старый и новый
    результат. Данные — только симуляция, внешних действий нет.
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


def given_dispatch(state, command):
    """GIVEN: корректная обычная отправка; независима от XL-A14."""
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
        state и command имеют формат XL-A14: события, next_id и каноническая
        команда create_event или join_event. mode гарантированно равен
        'apply' либо 'preview'. Для корректного обычного выполнения вызывай
        given_dispatch; эта задача от XL-A14 не зависит.

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
