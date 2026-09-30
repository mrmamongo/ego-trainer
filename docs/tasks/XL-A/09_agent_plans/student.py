"""XL-A / 09. Планы агента — задачи XL-A25, XL-A26, XL-A27.

Состояние сервиса: {events: {id: {title, capacity, members: [str]}},
announcements: [{event_id, text}], next_id: int}. Следующий свободный ID
имеет вид e<next_id>; счётчик растёт только при успешном создании.
Команда: {tool: str, args: dict}. Все операции чистые: входное состояние
и аргументы сохраняются. Событие создают, в него вступают и объявляют о нём.
Все задачи используют стандартную библиотеку, без сетевых вызовов.
Состояние имеет ровно перечисленные поля, его записи корректны.
command содержит tool (строку) и args (словарь). Простые значения args —
str, int, bool или None. В XL-A26/27 также разрешены словари-ссылки.
"""


def task_xla25_run_action(state, command):
    """XL-A25. ПРАВКИ — разложить обработчик команды на части.

    Текущий обработчик — читаемый, но длинный монолит. Раздели его на
    небольшие функции нормализации/проверки и выполнения, сохранив весь
    договор. Самостоятельные помощники можно определить ниже; публичная
    точка входа и её результат должны остаться прежними.

    Верни {status: "done" или "rejected", state: глубокая копия,
    result: dict или None, reason: строка или None}. Сначала проверяется
    tool: неизвестное имя даёт unknown_tool. create_event: title должен
    быть непустой строкой после strip, иначе invalid_title; capacity —
    именно int >= 1 (bool не подходит), иначе invalid_capacity. Успех
    создаёт e<next_id>, пустых участников, увеличивает next_id и возвращает
    {event_id}. join_event: сначала неизвестное событие -> unknown_event;
    member_id — непустая строка без обрезки, иначе invalid_member; затем
    повторное участие -> already_joined; затем заполненное событие ->
    event_full. Успех добавляет участника и возвращает event_id/member_id.
    prepare_announcement: сначала unknown_event; text после strip должен
    быть непустым, иначе invalid_text. Успех добавляет объявление и
    возвращает его нулевой индекс announcement_index. Любой отказ
    оставляет state прежним и возвращает result=None.

    Примеры: при next_id=4 создание " Raid " capacity=2 даёт e4,
    title="Raid", next_id=5. Повторное вступление одного игрока даёт
    already_joined; второму игроку при capacity=1 — event_full. Пустой
    текст объявления даёт invalid_text и не добавляет запись. Проверь
    каждый приоритет ошибок и неизменность входов.

    Ниже полная работающая версия — референс поведения для рефакторинга.
    Рекомендуемые роли помощников: нормализация, валидация, исполнение,
    упаковка результата. Сложность разбиения оценит наставник отдельно.

    Проверяемые примеры:
        state = {"events": {}, "announcements": [], "next_id": 4}
        command = {"tool": "create_event", "args": {"title": " Raid ", "capacity": 2}}
        assert task_xla25_run_action(state, command) == {
            "status": "done",
            "state": {"events": {"e4": {"title": "Raid", "capacity": 2, "members": []}},
                      "announcements": [], "next_id": 5},
            "result": {"event_id": "e4"}, "reason": None}
        command = {"tool": "create_event", "args": {"title": " ", "capacity": 0}}
        assert task_xla25_run_action(state, command) == {
            "status": "rejected", "state": state, "result": None, "reason": "invalid_title"}
    """
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
        title = args.get("title")
        capacity = args.get("capacity")
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
        event_id = args.get("event_id")
        member_id = args.get("member_id")
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
        event_id = args.get("event_id")
        text = args.get("text")
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


# GIVEN: независимая рабочая реализация одной команды для XL-A26/27.
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


# GIVEN: разрешить scalar/ref аргументы слева направо; вернуть (args, error).
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


def task_xla27_resume_plan(state, steps, completed):
    """XL-A27. НАЙТИ БАГ — возобновить план после перезапуска агента.

    После остановки процесса сервер сохранил состояние и результаты
    успешных шагов. Исправь возобновление так, чтобы уже выполненные
    действия не выполнялись повторно, а следующие ссылки могли использовать
    сохранённый результат. План тот же; completed содержит step_id -> dict
    результата успешного шага. ID известны плану, результаты согласованы с
    ним; сохранённые шаги могут быть разрознены из-за некритичных отказов.

    Повторно использованный шаг получает status="reused", исходный result,
    reason=None. Он не исполняется. Новые успехи получают done и добавляются
    в возвращаемую completed; отказы туда не попадают. Используй правила
    XL-A26 для ссылок, error при отсутствующем поле, dependency_failed,
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
