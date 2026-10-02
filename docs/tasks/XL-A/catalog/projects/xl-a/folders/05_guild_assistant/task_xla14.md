---
id: XL-A14
title: "отказное действие выглядит успешным"
version: "1.0.0"
level: medium
tags: ["guild-assistant", "bug"]
folder: 05_guild_assistant
---

# Задача XL-A14: отказное действие выглядит успешным

**Блок:** XLA05 — Помощник гильдии

**Сложность:** medium

**Темы:** guild-assistant, bug

## Условие

**Формат работы:** НАЙТИ БАГ

### Общий договор данных

Работаем с безопасной подготовкой и симуляцией игровых действий.
Все данные локальны: функция не обращается к сети, модели или игре.
Аргументы не меняются. Задачи независимы, а GIVEN-помощники можно
вызывать, но нельзя изменять.

### Задание

Симулятор событий уже умеет создавать событие и добавлять участника.
Обёртка должна различать успешный результат и штатный отказ обработчика.
Сейчас интерфейс может сообщить «готово», хотя участник не добавлен.
Исправь функцию, сохранив её сигнатуру и формат ответа.

**Аргументы:**

```text
state={events:[{id,title,capacity,members:[ID]}], next_id:int}.
command — каноническая команда: create_event с args {title,capacity}
или join_event с args {event_id,member_id}. next_id задаёт следующий
свободный номер eN. Используй подходящий GIVEN-обработчик.
```

Результат всегда содержит status, state, result, reason. При успехе
status='done', state — состояние обработчика, result — его value,
reason=None. При отказе status='rejected', state остаётся равным
исходному состоянию, result=None, reason — код отказа обработчика.
Неизвестный tool отклоняется с reason='unknown_tool'. Для join причины
проверяются обработчиком в порядке unknown_event, already_joined,
event_full. Успешное вступление добавляет member_id, а создание выдаёт
event_id. Входные объекты не меняй.

**Пример:**

```python
state={"events":[{"id":"e1","title":"Рейд","capacity":1,
                   "members":["m1"]}],"next_id":2}
command={"tool":"join_event","args":{"event_id":"e1","member_id":"m2"}}
task_xla14_dispatch(state, command) == {
    "status":"rejected","state":state,"result":None,"reason":"event_full"}
```

Второй пример: state={"events":[{"id":"e1","title":"Рейд",
"capacity":2,"members":[]}],"next_id":2}, та же команда для m2 даёт
{"status":"done","state":{"events":[{"id":"e1","title":"Рейд",
"capacity":2,"members":["m2"]}],"next_id":2},
"result":{"event_id":"e1","member_id":"m2"},"reason":None}.

Проверь также неизвестное событие, повторное вступление и неизвестный
tool. В сдаче укажи причину бага и пример, различающий старый и новый
результат. Данные — только симуляция, внешних действий нет.
