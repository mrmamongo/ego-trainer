---
id: mo-contains-bool
title: "__contains__ и __bool__: in и if для объектов"
order: 5
version: "1.0.0"
---

# `__contains__` и `__bool__`: `in` и `if` для объектов

## `in`

Выражение `x in obj` вызывает `obj.__contains__(x)`. Метод должен **вернуть** `True` или `False`.

```python
class Cart:
    def __init__(self, items):
        self.items = items                  # список названий

    def __contains__(self, name):
        return name in self.items

    def __len__(self):
        return len(self.items)

full = Cart(["чай", "хлеб"])                # 1
empty = Cart([])                            # 2
a = "чай" in full                           # 3
b = "сыр" in full                           # 4
c = bool(full)                              # 5
d = bool(empty)                             # 6
```

| Строка | Результат | Почему |
|---|---|---|
| 3 | `True` | `full.__contains__("чай")` |
| 4 | `False` | такого товара нет |
| 5 | `True` | у `Cart` нет `__bool__`, Python берёт `__len__`: `2` значит правда |
| 6 | `False` | `__len__` вернул `0`, а `0` это «ложь» |

## `if obj` и `__bool__`

Условие `if obj:` и функция `bool(obj)` спрашивают у объекта: «ты правдив?». Порядок поиска такой:

1. Если есть `__bool__`, Python вызывает его (метод обязан вернуть `True` или `False`).
2. Иначе, если есть `__len__`, правдив тот, у кого длина не ноль.
3. Иначе объект всегда правдив.

Поэтому пустая корзина с `__len__` сама оказывается ложью, и `if cart:` читается как «если в корзине что-то есть». Свой `__bool__` нужен, когда смысл «пустоты» другой: например, корзина из одних бесплатных товаров тоже «пуста».

```python
def __bool__(self):
    return any(price > 0 for _, price in self.items)
```

## Частые ошибки

`__contains__` без `return`: метод вернёт `None`, и `in` всегда даст `False`, даже если товар лежит в корзине.

`__bool__`, который возвращает список или число вместо `True`/`False`: Python ответит `TypeError`.

Забыть, что без `__len__` и `__bool__` любой объект правдив: `if Cart():` будет `True` даже для пустой корзины.

## Проверь себя

```python
class Box:
    def __init__(self, things):
        self.things = things

    def __len__(self):
        return len(self.things)

b = Box([])
```

1. Чему равно `bool(b)`?
2. Что изменится, если добавить `def __bool__(self): return True`?
3. Что даст `"x" in b`?

<details><summary>Ответ</summary>

1. `False`: длина `0`.
2. `bool(b)` станет `True`, потому что `__bool__` важнее `__len__`.
3. `TypeError`: у `Box` нет `__contains__`, и Python не знает, как искать внутри. Перебор объекта в цикле (`__iter__`) будет в следующей папке.

</details>
