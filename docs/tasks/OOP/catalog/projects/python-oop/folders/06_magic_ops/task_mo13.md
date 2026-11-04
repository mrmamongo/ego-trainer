---
id: MO13
title: "Очки раундов через sum"
version: "1.0.0"
level: medium
tags: [magic, write, radd, sum, score]
breaking: false
theory: [mo-radd-sum, mo-notimplemented]
---

# Задача MO13: Очки раундов через sum

## Условие

### Как это работает

Чтобы `sum([Score(5), Score(7)])` работал, нужны два метода: `__add__` для сложения двух объектов и `__radd__` для первого шага `0 + Score(5)`.

```python
def __radd__(self, other):
    if other == 0:
        return self
    return NotImplemented
```

| Выражение | Результат |
|---|---|
| `sum([Score(5), Score(7)])` | `Score` с `points` равным `12` |
| `sum([])` | число `0` |
| `sum([Score(1)], 10)` | `TypeError`: начало `10`, а не `0` |

### Задание

Напиши класс `Score` с атрибутом `points`: `__add__(other)` складывает два `Score` (для чужого типа возвращает `NotImplemented`), а `__radd__(other)` принимает только `0` и возвращает `self`, иначе возвращает `NotImplemented`.

## Аргументы

- `points` — список очков за раунды (может быть пустым).
- `start` — число, с которого начинает `sum` (`0` или другое).

## Возвращает

Сумма очков (число). Если `sum` закончился `TypeError`, то строка `"TypeError"`. Для пустого списка результат это само число `start`.

## Правила

- Пиши только класс `Score`; рамку внизу файла не трогай.
- Нужны методы `__init__`, `__add__` и `__radd__`.
- `__radd__` принимает только `0`.

## Пример

```python
task_mo13_total([3, 4, 5], 0)   # -> 12
task_mo13_total([3, 4], 5)       # -> "TypeError"
task_mo13_total([], 0)           # -> 0
```

## Учебные цели

- Написать пару `__add__` и `__radd__`, чтобы работал `sum`.
- Возвращать `NotImplemented` для всего лишнего.

## Проверка понимания

Почему `sum([Score(1)], 10)` падает? Что даст `sum([Score(1), Score(2)])`, если `__radd__` будет возвращать `Score(self.points + other)`?
