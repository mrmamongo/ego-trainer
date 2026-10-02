---
id: XL-A05
title: "награда выдаётся повторно"
version: "1.0.0"
level: medium
tags: ["quest-journal", "bug"]
folder: 02_quest_journal
---

# Задача XL-A05: награда выдаётся повторно

**Блок:** XLA02 — Квестовый журнал

**Сложность:** medium

**Темы:** quest-journal, bug

## Условие

**Формат работы:** НАЙТИ БАГ

### Общий договор данных

Все ID и названия — строки. Числа — целые. Входные объекты менять нельзя.
Каждая задача самостоятельна и содержит собственный договор данных.
В баговой задаче сдай исправление, причину и воспроизводящий пример.
В задаче на правки проверь старый простой случай и новые требования.

### Задание

Игрок дважды нажал «Забрать». Исправь код, чтобы один квест
приносил награду только один раз, включая последовательные вызовы.

**Вход:**

```text
player = {"gold": 10, "completed": ["q1"], "claimed": []}.
rewards = {"q1": 5, "q2": 20}; значения — золото >= 0.
completed и claimed — списки уникальных ID; claimed входит в completed.
```

Результат: {"status": строка, "player": новое состояние}.
**Проверки строго в таком порядке:**

```text
1. quest_id нет в rewards -> "unknown_quest".
2. Награда уже в claimed -> "already_claimed".
3. quest_id нет в completed -> "not_completed".
4. Иначе -> "claimed": прибавить золото, дописать ID в конец claimed.
```

completed не меняется. При любом отказе состояние равно исходному.
Входной player, в том числе его списки, изменять нельзя.

**Пример:**

```text
first = task_xla05_claim_reward(
    {"gold": 10, "completed": ["q1"], "claimed": []}, "q1", {"q1": 5})
Ожидаем:
    {"status": "claimed", "player":
     {"gold": 15, "completed": ["q1"], "claimed": ["q1"]}}.
Второй вызов с first["player"] -> status="already_claimed",
gold остаётся 15, claimed остаётся ["q1"].
Запрос неизвестного q9 -> unknown_quest, всё состояние прежнее.

assert task_xla05_claim_reward(first["player"], "q1", {"q1": 5}) == {
    "status": "already_claimed", "player": first["player"]}
assert task_xla05_claim_reward(first["player"], "q9", {"q1": 5}) == {
    "status": "unknown_quest", "player": first["player"]}
```

Проверь также нулевую награду и известный, но незавершённый квест.
Пример повторного вызова должен входить в твою проверку исправления.
