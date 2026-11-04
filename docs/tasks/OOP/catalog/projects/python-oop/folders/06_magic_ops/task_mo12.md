---
id: MO12
title: "Деньги и чужие типы"
version: "1.0.0"
level: medium
tags: [magic, write, notimplemented, money]
breaking: false
theory: [mo-notimplemented, mo-arith]
---

# Задача MO12: Деньги и чужие типы

## Условие

### Как это работает

Складывать деньги можно только с деньгами. Для другого типа метод `__add__` должен вернуть `NotImplemented`, и Python сам превратит это в `TypeError`:

```python
def __add__(self, other):
    if not isinstance(other, Money):
        return NotImplemented
    return Money(self.kopecks + other.kopecks)
```

| Выражение | Результат |
|---|---|
| `Money(100) + Money(50)` | `Money(150)` |
| `Money(100) + 5` | `TypeError` |
| `5 + Money(100)` | `TypeError`: число не умеет, а `__radd__` у `Money` нет |

### Задание

Напиши класс `Money`: `__init__(kopecks)` запоминает `kopecks`, `__add__(other)` складывает с другим `Money` и возвращает новый, а для любого другого типа **возвращает** `NotImplemented`. Рамка проверяет и результат, и то, что `__add__` именно вернул `NotImplemented`, а не бросил ошибку сам.

## Аргументы

- `rows` — список четвёрок `[копейки, вид, значение, наоборот]`. Вид `"money"` значит, что второй операнд `Money(значение)`, иначе это само значение. Если `наоборот` равно `True`, пример считается как `второй + первый`.

## Возвращает

Список результатов по одному на четвёрку: `[итог, прямой_ответ]`. Итог — копейки суммы или `"TypeError"`. Прямой ответ — `True`, если вызов `Money(копейки).__add__(второй)` вернул `NotImplemented`.

## Правила

- Пиши только класс `Money`; рамку внизу файла не трогай.
- Нужны методы `__init__` и `__add__`.
- Для чужого типа **верни** `NotImplemented`, не бросай ошибку сам.

## Пример

```python
task_mo12_add([[100, "money", 50, False], [100, "number", 5, False]])
# -> [[150, False], ["TypeError", True]]
```

## Учебные цели

- Проверять тип в `__add__` и возвращать `NotImplemented`.
- Понимать, что `число + Money` без `__radd__` тоже `TypeError`.

## Проверка понимания

Почему `5 + Money(100)` падает, хотя `Money(100) + 5` уже обработан? Чем `return NotImplemented` отличается от `raise TypeError`?
