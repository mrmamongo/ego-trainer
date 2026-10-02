---
id: XL-A26
title: "выполнить план с передачей результатов"
version: "1.0.0"
level: hard
tags: ["agent-plans", "new"]
folder: 09_agent_plans
---

# Задача XL-A26: выполнить план с передачей результатов

**Блок:** XLA09 — Планы агента

**Сложность:** hard

**Темы:** agent-plans, new

## Условие

**Формат работы:** НОВЫЙ КОД

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

### Задание

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
**Полный пример для state={"events":{},"announcements":[],"next_id":1}:**
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

**Полный вызов для самостоятельной проверки после реализации:**

```python
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
```

**Отдельный пример остановки:**

```text
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
```
