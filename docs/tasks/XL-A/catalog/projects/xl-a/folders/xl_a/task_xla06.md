---
id: XL-A06
title: "квест с несколькими целями"
version: "1.1.0"
level: medium
tags: ["quest-journal", "modify"]
folder: xl_a
---

# Задача XL-A06: квест с несколькими целями

**История:** XLA02 — Квестовый журнал

**Сложность:** medium

**Темы:** quest-journal, modify

## Условие

**Формат работы:** ПРАВКИ

### Общий договор данных

Все ID и названия — строки, числа — целые. Входные объекты менять нельзя.
Каждая задача самостоятельна: всё, что нужно для решения, есть в её условии.
В задаче с ошибкой сдай исправление, объяснение причины
и пример, на котором ошибка воспроизводится.
В задаче на доработку проверь и старый простой случай, и новые требования.

### Задание

Сейчас обработчик умеет вести одну цель квеста. Расширь его для квестов
вида «победи волков И собери травы», сохранив прежнее поведение для
квеста с одной целью.

**Что приходит на вход:**

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
Обрабатывай события по порядку. Известной цели прибавь amount,
но progress не должен уйти выше её target. Остальные цели не трогай.
Неизвестную цель пропусти и добавь индекс события в rejected.
completed=True только тогда, когда достигнуты ВСЕ цели.
Квест без целей считается завершённым; все его события неизвестны.
Порядок целей и дополнительные поля quest сохрани.
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
завершённый квест; то, что исходный quest остался прежним.
