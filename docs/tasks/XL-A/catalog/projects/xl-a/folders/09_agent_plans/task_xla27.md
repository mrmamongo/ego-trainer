---
id: XL-A27
title: "возобновить план после перезапуска агента"
version: "1.0.0"
level: hard
tags: ["agent-plans", "bug"]
folder: 09_agent_plans
---

# Задача XL-A27: возобновить план после перезапуска агента

**Блок:** XLA09 — Планы агента

**Сложность:** hard

**Темы:** agent-plans, bug

## Условие

**Формат работы:** НАЙТИ БАГ

### Общий договор данных

Состояние сервиса: {events: {id: {title, capacity, members: [str]}},
announcements: [{event_id, text}], next_id: int}. Следующий свободный ID
имеет вид e<next_id>; счётчик растёт только при успешном создании.
Команда: {tool: str, args: dict}. Все операции чистые: входное состояние
и аргументы сохраняются. Событие создают, в него вступают и объявляют о нём.
Все задачи используют стандартную библиотеку, без сетевых вызовов.
Состояние имеет ровно перечисленные поля, его записи корректны.
command содержит tool (строку) и args (словарь). Простые значения args —
str, int, bool или None. В аргументах шагов также разрешены словари-ссылки.

### Дополнительный договор данных

**Команды GIVEN given_run_action:**
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

**Данные плана и правила выполнения:**

```python
step = {"id": "join", "tool": "join_event", "critical": True,
        "args": {"event_id": {"from_step": "create", "field": "event_id"},
                 "member_id": "Sam"}}
report = {"id": "join", "status": "done", "result": {}, "reason": None}
```

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

### Задание

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

**Пример: state содержит e1 и next_id=2; completed={"create":**
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

**Проверяемый пример:**

```python
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
```

**Повторный вызов после успешного продолжения:**

```python
again = task_xla27_resume_plan(expected["state"], steps, expected["completed"])
assert again["state"] == expected["state"]
assert again["completed"] == expected["completed"]
assert [report["status"] for report in again["steps"]] == ["reused", "reused"]
assert again["ok"] is True
```
