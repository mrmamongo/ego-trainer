---
id: XL-A09
title: "один игрок занимает два места"
version: "1.0.0"
level: medium
tags: ["party-finder", "bug"]
folder: 03_party_finder
---

# Задача XL-A09: один игрок занимает два места

**Блок:** XLA03 — Поиск группы в MMO

**Сложность:** medium

**Темы:** party-finder, bug

## Условие

**Формат работы:** НАЙТИ БАГ

### Общий договор данных

Роли: tank, healer, damage. У игрока ровно одна роль.
Все количества, уровни и время ожидания — целые >= 0.
Чем больше wait_seconds, тем дольше игрок ждёт.
Входные данные менять нельзя. Задачи независимы.
Для бага подготовь объяснение и воспроизводящий пример.

### Дополнительный договор данных

**Места и результат подбора:**

```python
slots = {"tank": 1, "healer": 1, "damage": 2}
result = {"members": [ID],
          "missing": {"tank": int, "healer": int, "damage": int},
          "ready": bool}
```

Количество мест — целое >= 0. Отсутствующая в slots роль требует 0 мест.
Роли обрабатываются в порядке tank, healer, damage. Внутри роли сначала
выбирается большее wait_seconds, при равенстве — меньший по алфавиту ID
игрока. members следует этому порядку. При нехватке сохраняется частичный
состав. В missing всегда все три роли и число незаполненных мест каждой.
ready=True ровно при отсутствии незаполненных мест. Для slots={}
members=[], все значения missing равны 0, ready=True.

### Задание

Пользователь несколько раз нажал поиск, и сервис создал разные заявки
на одного игрока. Исправь подборщик: повторная заявка не даёт нового места.

**Вход:**

```text
tickets = [{"ticket_id": "r1", "player_id": "A",
            "role": "tank", "wait_seconds": 30}, ...].
ticket_id уникальны. У заявок одного player_id одинаковые role
и wait_seconds. Форматы slots и результата приведены в договоре данных этой задачи.
```

**Правила:**

```text
Каждый player_id участвует в отборе один раз.
Приоритет определяется wait_seconds, затем player_id, а не ticket_id.
Порядок ролей: tank, healer, damage. Вернуть частичный состав,
если уникальных игроков не хватает.
```

**Пример:**

```text
tickets = [{"ticket_id": "r1", "player_id": "A", "role": "tank", "wait_seconds": 30},
           {"ticket_id": "r2", "player_id": "A", "role": "tank", "wait_seconds": 30}]
slots={"tank": 2} ->
    {"members": ["A"],
     "missing": {"tank": 1, "healer": 0, "damage": 0}, "ready": False}.
Если добавить B/tank/wait_seconds=20, состав станет ["A", "B"].

assert task_xla09_party_from_tickets(tickets, {"tank": 2}) == {
    "members": ["A"],
    "missing": {"tank": 1, "healer": 0, "damage": 0}, "ready": False}
assert task_xla09_party_from_tickets(tickets, {}) == {
    "members": [],
    "missing": {"tank": 0, "healer": 0, "damage": 0}, "ready": True}
```

Проверь дубликаты не рядом, три заявки одного игрока и очередь без
повторов. Перестановка одинаковых по смыслу заявок не меняет ответ.
Объясни, что именно в предметной области должно быть уникальным.
