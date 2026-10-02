---
id: XL-A25
title: "разложить обработчик команды на части"
version: "1.0.0"
level: hard
tags: ["agent-plans", "modify"]
folder: 09_agent_plans
---

# Задача XL-A25: разложить обработчик команды на части

**Блок:** XLA09 — Планы агента

**Сложность:** hard

**Темы:** agent-plans, modify

## Условие

**Формат работы:** ПРАВКИ

### Общий договор данных

Состояние сервиса: {events: {id: {title, capacity, members: [str]}},
announcements: [{event_id, text}], next_id: int}. Следующий свободный ID
имеет вид e<next_id>; счётчик растёт только при успешном создании.
Команда: {tool: str, args: dict}. Все операции чистые: входное состояние
и аргументы сохраняются. Событие создают, в него вступают и объявляют о нём.
Все задачи используют стандартную библиотеку, без сетевых вызовов.
Состояние имеет ровно перечисленные поля, его записи корректны.
command содержит tool (строку) и args (словарь). Простые значения args —
str, int, bool или None.

### Задание

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

**Проверяемые примеры:**

```python
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
```
