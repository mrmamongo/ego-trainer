---
id: XL-A06
title: "квест с несколькими целями"
version: "1.0.0"
level: medium
tags: ["quest-journal", "modify"]
folder: 02_quest_journal
---

# Задача XL-A06: квест с несколькими целями

**Блок:** XLA02 — Квестовый журнал

**Сложность:** medium

**Темы:** quest-journal, modify

## Условие

**Формат работы:** ПРАВКИ

### Общий договор данных

Все ID и названия — строки. Числа — целые. Входные объекты менять нельзя.
Каждая задача самостоятельна и содержит собственный договор данных.
В баговой задаче сдай исправление, причину и воспроизводящий пример.
В задаче на правки проверь старый простой случай и новые требования.

### Задание

Сейчас обработчик поддерживает одну цель. Расширь его для квеста
«победи волков И собери травы», сохранив старый случай одной цели.

**Вход:**

```text
quest = {"id": "q1", "objectives": [
    {"id": "wolves", "target": 3, "progress": 1},
    {"id": "herbs", "target": 5, "progress": 0}] }.
У целей уникальные id, target > 0, 0 <= progress <= target.
events = [{"objective_id": "wolves", "amount": 2}, ...].
amount >= 0. События могут повторяться и ссылаться на неизвестную цель.
```

**Правила:**

```text
Обрабатывать события по порядку. Известной цели прибавить amount,
ограничив progress её target. Остальные цели не трогать.
Неизвестную цель пропустить, добавить индекс события в rejected.
completed=True, только если достигнуты ВСЕ цели.
Квест без целей считается завершённым; все его события неизвестны.
Порядок целей и дополнительные поля quest сохранить.
```

**Верни:**

```text
{"quest": новое состояние, "completed": bool, "rejected": [индексы]}.
```

**Пример для quest выше:**

```text
events = [{"objective_id": "wolves", "amount": 10},
          {"objective_id": "ghost", "amount": 1},
          {"objective_id": "herbs", "amount": 4}]
-> progress: wolves=3, herbs=4; completed=False; rejected=[1].
Ещё одно событие herbs с amount=1 на обновлённом квесте
-> wolves=3, herbs=5; completed=True; rejected=[].
events=[] -> неизменный квест и completed по его текущим целям.

single = {"id": "q", "objectives": [
    {"id": "herbs", "target": 2, "progress": 1}]}
assert task_xla06_advance_quest(single, [
    {"objective_id": "herbs", "amount": 3}]) == {
    "quest": {"id": "q", "objectives": [
        {"id": "herbs", "target": 2, "progress": 2}]},
    "completed": True, "rejected": []}
assert task_xla06_advance_quest(single, []) == {
    "quest": single, "completed": False, "rejected": []}
```

Проверь: одну цель; несколько событий одной цели; превышение target;
завершённый квест; отсутствие изменений в исходном quest.
