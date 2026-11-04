---
id: mo-notimplemented
title: "NotImplemented: что делать с чужим типом"
order: 2
version: "1.0.0"
---

# `NotImplemented`: что делать с чужим типом

А что будет, если сложить деньги с числом или строкой: `Money(100) + 5`? Внутри `__add__` мы пишем `other.kopecks`, а у числа `5` такого атрибута нет. Получится невнятный `AttributeError`.

Правильно проверить тип в начале метода и для чужого типа вернуть специальное значение `NotImplemented`. Оно значит: «я не умею складываться с таким, спроси другую сторону».

```python
class Money:
    def __init__(self, kopecks):
        self.kopecks = kopecks

    def __add__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return Money(self.kopecks + other.kopecks)

a = Money(100)             # 1
b = a + Money(20)          # 2
c = a + 5                  # 3
```

| Строка | Что произошло |
|---|---|
| 2 | `other` это `Money`, вернулся новый объект со `120` копейками |
| 3 | `__add__` вернул `NotImplemented`, Python спросил у числа `5`, тот тоже не умеет, итог: `TypeError: unsupported operand type(s) for +` |

То есть `NotImplemented` в итоге превращается в понятную ошибку `TypeError`, а не в молчаливый мусор.

## Частые ошибки

Вернуть вместо этого `None`, `False` или `0`:

```python
def __add__(self, other):
    if not isinstance(other, Money):
        return None                 # Money(100) + 5 даст None без всякой ошибки
    return Money(self.kopecks + other.kopecks)
```

Ошибки не будет, а в переменной окажется `None`. Через несколько строк программа упадёт в другом месте, и найти причину будет трудно.

Ещё путают `NotImplemented` (значение, его **возвращают**) и `NotImplementedError` (исключение, его бросают через `raise`). Для арифметики нужно первое.

## Проверь себя

```python
class Score:
    def __init__(self, points):
        self.points = points

    def __add__(self, other):
        if not isinstance(other, Score):
            return NotImplemented
        return Score(self.points + other.points)
```

1. Что даст `Score(1) + Score(2)`?
2. Что даст `Score(1) + "2"`?
3. Что будет, если в проверке вместо `NotImplemented` написать `return None`?

<details><summary>Ответ</summary>

1. Новый `Score` с `points` равным `3`.
2. `TypeError`: `__add__` вернул `NotImplemented`, и строка тоже не умеет складываться со `Score`.
3. Ошибки не будет: выражение молча даст `None`.

</details>
