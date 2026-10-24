"""
XL-A27. НАЙТИ БАГ — возобновить план после перезапуска агента.

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

Данные плана и правила выполнения:
    step = {"id": "join", "tool": "join_event", "critical": True,
            "args": {"event_id": {"from_step": "create", "field": "event_id"},
                     "member_id": "Sam"}}
    report = {"id": "join", "status": "done", "result": {}, "reason": None}

steps — список шагов в порядке выполнения. id — уникальная строка;
critical — bool. Значения args — str, int, bool, None либо одноуровневая
ссылка {from_step: id, field: имя_поля} на более ранний шаг. Поле результата
может отсутствовать. Аргументы просматриваются в порядке вставки: первая
ошибка ссылки определяет отказ. given_resolve_args возвращает (args, error).
Неуспешная зависимость даёт dependency_failed:<id>; отсутствующее поле —
missing_result_field:<id>:<field>. Такой шаг получает rejected, result=None.
Разрешённые аргументы передаются в given_run_action. Успех имеет done,
result команды и reason=None; отказ — rejected, result=None и reason команды.
Отказ не меняет состояние. После некритичного отказа выполнение продолжается.
После critical-отказа все следующие шаги получают skipped, result=None,
reason=stopped_after:<упавший_id>. Отчёты сохраняют порядок исходных шагов.
Пустой план успешен. Правила reused и возвращаемого completed приведены
в условии возобновления ниже.

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


def task_xla27_resume_plan(state, steps, completed):
    """
    XL-A27. НАЙТИ БАГ — возобновить план после перезапуска агента.

    После остановки процесса сервер сохранил состояние и результаты
    успешных шагов. Исправь возобновление так, чтобы уже выполненные
    действия не выполнялись повторно, а следующие ссылки могли использовать
    сохранённый результат. План тот же; completed содержит step_id -> dict
    результата успешного шага. ID известны плану, результаты согласованы с
    ним; сохранённые шаги могут быть разрознены из-за некритичных отказов.

    Повторно использованный шаг получает status="reused", исходный result,
    reason=None. Он не исполняется.
    Сохранённый результат используется до разрешения args: у reused-шага
    аргументы и ссылки повторно не проверяются. Например, его зависимость
    может получить некритический отказ в текущем проходе, но сохранённый
    результат самого шага всё равно остаётся пригодным для повторного использования.
    Новые успехи получают done и добавляются в возвращаемую completed;
    отказы туда не попадают. Используй правила из договора данных этой задачи для ссылок,
    error при отсутствующем поле, dependency_failed,
    критического отказа и skipped. Возвращай {state, steps, completed, ok};
    ok допускает только done/reused. Входные state, steps, completed нельзя
    менять. Ссылки разрешаются как из сохранённых, так и из новых результатов.

    Пример: state содержит e1 и next_id=2; completed={"create":
    {"event_id":"e1"}}. План create, затем join B со ссылкой на create.
    Отчёт create — reused; B вступает в e1; next_id остаётся 2. При
    повторном запуске с обоими результатами cached-отчёты все reused,
    состояние не меняется. Ошибочные шаги не кешируются; их можно
    попробовать снова. Проверь также сохранённый успешный шаг после
    раннего некритичного отказа.

    При новом critical-отказе остановка имеет приоритет: все последующие
    шаги skipped, даже если у них есть completed; кеш сохраняется, состояние
    уже выполненного не откатывается. Иначе успешный кешированный шаг reused.

    Воспроизводимый симптом исходника: он возвращает дубликатное действие
    и расходует следующий ID. Исправь, сохранив остальную обработку плана.

    Проверяемый пример:
        state = {"events": {"e1": {"title": "Raid", "capacity": 2, "members": []}},
                 "announcements": [], "next_id": 2}
        steps = [
            {"id": "create", "tool": "create_event", "critical": True,
             "args": {"title": "Raid", "capacity": 2}},
            {"id": "join", "tool": "join_event", "critical": True,
             "args": {"event_id": {"from_step": "create", "field": "event_id"}, "member_id": "B"}}]
        completed = {"create": {"event_id": "e1"}}
        expected = {
            "state": {"events": {"e1": {"title": "Raid", "capacity": 2, "members": ["B"]}},
                      "announcements": [], "next_id": 2},
            "steps": [
                {"id": "create", "status": "reused", "result": {"event_id": "e1"}, "reason": None},
                {"id": "join", "status": "done", "result": {"event_id": "e1", "member_id": "B"}, "reason": None}],
            "completed": {"create": {"event_id": "e1"}, "join": {"event_id": "e1", "member_id": "B"}},
            "ok": True}
        assert task_xla27_resume_plan(state, steps, completed) == expected

    Повторный вызов после успешного продолжения:
        again = task_xla27_resume_plan(expected["state"], steps, expected["completed"])
        assert again["state"] == expected["state"]
        assert again["completed"] == expected["completed"]
        assert [report["status"] for report in again["steps"]] == ["reused", "reused"]
        assert again["ok"] is True
    """
    saved = dict(completed)
    reports = []
    results = {}
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
    stopped = None
    for step in steps:
        step_id = step["id"]
        if stopped is not None:
            reports.append(
                {
                    "id": step_id,
                    "status": "skipped",
                    "result": None,
                    "reason": "stopped_after:" + stopped,
                }
            )
            continue
        args, error = given_resolve_args(step["args"], results)
        if error is None:
            action = given_run_action(updated, {"tool": step["tool"], "args": args})
            updated = action["state"]
            if action["status"] == "done":
                result = action["result"]
                status, reason = "done", None
                saved[step_id] = result
            else:
                result, status, reason = None, "rejected", action["reason"]
        else:
            result, status, reason = None, "rejected", error
        reports.append({"id": step_id, "status": status, "result": result, "reason": reason})
        if status == "done":
            results[step_id] = result
        elif step["critical"]:
            stopped = step_id
    return {
        "state": updated,
        "steps": reports,
        "completed": saved,
        "ok": all(report["status"] in ("done", "reused") for report in reports),
    }
