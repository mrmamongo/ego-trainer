---
id: XL-A08
title: "собрать пати по заявкам"
version: "1.0.0"
level: medium
tags: ["party-finder", "new"]
folder: 03_party_finder
---

# Задача XL-A08: собрать пати по заявкам

**Блок:** XLA03 — Поиск группы в MMO

**Сложность:** medium

**Темы:** party-finder, new

## Условие

**Формат работы:** НОВЫЙ КОД

### Общий договор данных

Роли: tank, healer, damage. У игрока ровно одна роль.
Все количества, уровни и время ожидания — целые >= 0.
Чем больше wait_seconds, тем дольше игрок ждёт.
Входные данные менять нельзя. Задачи независимы.
Для бага подготовь объяснение и воспроизводящий пример.

### Задание

Фильтры уже применены. Теперь нужно заполнить места по ролям.
В этой задаче ID игроков уникальны; смены и совмещения ролей нет.

**Вход:**

```text
players = [{"id": "A", "role": "tank", "wait_seconds": 30}, ...].
slots = {"tank": 1, "healer": 1, "damage": 2}.
В slots могут отсутствовать роли: для них требуется 0 мест.
```

**Правила:**

```text
Роли заполняются в порядке tank, healer, damage.
Внутри роли раньше берём того, кто дольше ждёт.
При одинаковом ожидании — меньший по алфавиту id.
Можно использовать given_order_candidates.
В members сначала танки, затем лекари, затем бойцы.
При нехватке игроков верни частичный состав, не обнуляй его.
```

**Результат:**

```text
{"members": [ID],
 "missing": {"tank": int, "healer": int, "damage": int},
 "ready": bool}.
Все роли в missing обязательны, даже с нулевым значением.
ready=True, когда нет незаполненных мест. Для slots={} это True.
```

**Пример:**

```text
players = [{"id": "T", "role": "tank", "wait_seconds": 10},
           {"id": "B", "role": "damage", "wait_seconds": 20},
           {"id": "A", "role": "damage", "wait_seconds": 20}]
slots={"tank": 1, "healer": 1, "damage": 1}
-> {"members": ["T", "A"],
    "missing": {"tank": 0, "healer": 1, "damage": 0}, "ready": False}.
slots={} -> members=[], все missing=0, ready=True.

assert task_xla08_build_party(players, {"tank": 1, "healer": 1, "damage": 1}) == {
    "members": ["T", "A"],
    "missing": {"tank": 0, "healer": 1, "damage": 0}, "ready": False}
assert task_xla08_build_party([], {}) == {
    "members": [],
    "missing": {"tank": 0, "healer": 0, "damage": 0}, "ready": True}
```

Проверь равное ожидание, лишних кандидатов, нулевые места и пустую очередь.
