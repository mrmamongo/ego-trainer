"""
XL-A26. НОВЫЙ КОД — выполнить план с передачей результатов.

Состояние сервиса: {events: {id: {title, capacity, members: [str]}},
announcements: [{event_id, text}], next_id: int}. Следующий свободный ID
имеет вид e<next_id>; счётчик растёт только при успешном создании.
Команда: {tool: str, args: dict}. Все операции чистые: входное состояние
и аргументы сохраняются. Событие создают, в него вступают и объявляют о нём.
Все задачи используют стандартную библиотеку, без сетевых вызовов.
Состояние имеет ровно перечисленные поля, его записи корректны.
command содержит tool (строку) и args (словарь). Простые значения args —
str, int, bool или None. В аргументах шагов также разрешены словари-ссылки.

Дополнительный договор данных

Команды GIVEN given_run_action:
- create_event: args={title, capacity}. title — непустая строка после strip,
  иначе invalid_title; capacity — именно int >= 1, bool не подходит,
  иначе invalid_capacity. Создаётся e<next_id> с пустыми members, счётчик
  увеличивается; result={event_id}.
- join_event: args={event_id, member_id}. Проверки по порядку: unknown_event;
  непустая строка member_id без обрезки, иначе invalid_member;
  already_joined; event_full. Успех добавляет участника,
  result={event_id, member_id}.
- prepare_announcement: args={event_id, text}. Сначала unknown_event,
  затем непустая строка text после strip, иначе invalid_text. Успех
  добавляет объявление; result={announcement_index}, индекс начинается с 0.

Неизвестный tool даёт unknown_tool. Результат одной команды содержит
{status, state, result, reason}. Успех: done и reason=None. Отказ: rejected,
result=None, reason — код ошибки; состояние остаётся прежним. Предметная
логика уже дана в given_run_action, её не нужно повторять.

Работай с этой функцией. GIVEN-помощники можно вызывать, но нельзя изменять.
"""


# GIVEN: готовый помощник для этой задачи.


def given_run_action(state, command):
    args = command.get("args", {})
    tool = command.get("tool")
    updated = {
        "events": {
            key: {
                "title": event["title"],
                "capacity": event["capacity"],
                "members": list(event["members"]),
            }
            for key, event in state["events"].items()
        },
        "announcements": [dict(item) for item in state["announcements"]],
        "next_id": state["next_id"],
    }
    result = None
    reason = None
    if tool == "create_event":
        title, capacity = args.get("title"), args.get("capacity")
        if not isinstance(title, str) or not title.strip():
            reason = "invalid_title"
        elif type(capacity) is not int or capacity < 1:
            reason = "invalid_capacity"
        else:
            event_id = "e" + str(updated["next_id"])
            updated["events"][event_id] = {
                "title": title.strip(),
                "capacity": capacity,
                "members": [],
            }
            updated["next_id"] += 1
            result = {"event_id": event_id}
    elif tool == "join_event":
        event_id, member_id = args.get("event_id"), args.get("member_id")
        if event_id not in updated["events"]:
            reason = "unknown_event"
        elif not isinstance(member_id, str) or not member_id:
            reason = "invalid_member"
        else:
            event = updated["events"][event_id]
            if member_id in event["members"]:
                reason = "already_joined"
            elif len(event["members"]) >= event["capacity"]:
                reason = "event_full"
            else:
                event["members"].append(member_id)
                result = {"event_id": event_id, "member_id": member_id}
    elif tool == "prepare_announcement":
        event_id, text = args.get("event_id"), args.get("text")
        if event_id not in updated["events"]:
            reason = "unknown_event"
        elif not isinstance(text, str) or not text.strip():
            reason = "invalid_text"
        else:
            index = len(updated["announcements"])
            updated["announcements"].append({"event_id": event_id, "text": text.strip()})
            result = {"announcement_index": index}
    else:
        reason = "unknown_tool"
    if reason is not None:
        return {"status": "rejected", "state": updated, "result": None, "reason": reason}
    return {"status": "done", "state": updated, "result": result, "reason": None}


# GIVEN: готовый помощник для этой задачи.


def given_resolve_args(args, results):
    resolved = {}
    for key, value in args.items():
        if isinstance(value, dict) and "from_step" in value:
            step_id, field = value["from_step"], value["field"]
            if step_id not in results:
                return None, "dependency_failed:" + step_id
            if field not in results[step_id]:
                return None, "missing_result_field:" + step_id + ":" + field
            resolved[key] = results[step_id][field]
        else:
            resolved[key] = value
    return resolved, None


def task_xla26_run_plan(state, steps):
    """XL-A26. НОВЫЙ КОД — выполнить план с передачей результатов.

    Агент составляет план из нескольких действий. Реализуй последовательное
    выполнение и ссылки на результаты предыдущих шагов. step имеет поля
    id (уникальная строка), tool, args и critical (bool). Значения args —
    scalar или ссылка {from_step: id, field: имя_поля}; ссылки ведут только
    на более ранние ID, они одноуровневые. Поле результата может отсутствовать.
    Перебирай аргументы в порядке вставки: первая ошибка ссылки определяет
    отказ шага. Для успешных шагов разрешай ссылки через given_resolve_args
    и вызывай given_run_action — предметную логику не копируй.

    Отчёт шага: {id, status, result, reason}. Успех — done, результат
    команды и reason=None. Отказ команды — rejected с её reason и result=None.
    Ссылка на отклонённый/неуспешный шаг: rejected,
    dependency_failed:<id>; отсутствующее поле: rejected,
    missing_result_field:<id>:<field>. После некритичного отказа продолжай;
    состояние отказавшего шага не меняется. После critical-отказа все
    последующие шаги получают skipped, result=None, reason=
    stopped_after:<упавший_id>. Верни {state, steps: reports, ok}; ok=True,
    только если все шаги done. Для пустого плана ok=True.

    Пример: create raid (capacity 2), join Sam с event_id из create,
    announce с тем же ID — три done; событие e1 содержит Sam и объявление.
    Полный пример для state={"events":{},"announcements":[],"next_id":1}:
    шаг create (create_event, title="Raid", capacity=2, critical=True),
    шаг join (join_event, event_id={"from_step":"create","field":"event_id"},
    member_id="Sam"), шаг announce (prepare_announcement, та же ссылка,
    text="Meet"). Результат: state={"events":{"e1":{"title":"Raid",
    "capacity":2,"members":["Sam"]}},"announcements":[{"event_id":"e1",
    "text":"Meet"}],"next_id":2}; все отчёты done, их result соответственно
    {"event_id":"e1"}, {"event_id":"e1","member_id":"Sam"},
    {"announcement_index":0}; ok=True. Если первый шаг join на e9
    noncritical, он rejected/unknown_event, следующий create X capacity=1
    будет done и создаст e1.

    Полный вызов для самостоятельной проверки после реализации:
        state = {"events": {}, "announcements": [], "next_id": 1}
        steps = [
            {"id": "create", "tool": "create_event", "critical": True,
             "args": {"title": "Raid", "capacity": 2}},
            {"id": "join", "tool": "join_event", "critical": True,
             "args": {"event_id": {"from_step": "create", "field": "event_id"}, "member_id": "Sam"}},
            {"id": "announce", "tool": "prepare_announcement", "critical": False,
             "args": {"event_id": {"from_step": "create", "field": "event_id"}, "text": "Meet"}}]
        assert task_xla26_run_plan(state, steps) == {
            "state": {"events": {"e1": {"title": "Raid", "capacity": 2, "members": ["Sam"]}},
                      "announcements": [{"event_id": "e1", "text": "Meet"}], "next_id": 2},
            "steps": [
                {"id": "create", "status": "done", "result": {"event_id": "e1"}, "reason": None},
                {"id": "join", "status": "done", "result": {"event_id": "e1", "member_id": "Sam"}, "reason": None},
                {"id": "announce", "status": "done", "result": {"announcement_index": 0}, "reason": None}],
            "ok": True}

    Отдельный пример остановки:
        steps = [
            {"id": "join", "tool": "join_event", "critical": True,
             "args": {"event_id": "e9", "member_id": "Sam"}},
            {"id": "create", "tool": "create_event", "critical": False,
             "args": {"title": "Raid", "capacity": 2}}]
        assert task_xla26_run_plan(state, steps) == {
            "state": state, "steps": [
                {"id": "join", "status": "rejected", "result": None, "reason": "unknown_event"},
                {"id": "create", "status": "skipped", "result": None, "reason": "stopped_after:join"}],
            "ok": False}
        Если critical первого шага поменять на False, create выполнится,
        создаст e1, но ok останется False из-за отказа join.
    """
    pass
