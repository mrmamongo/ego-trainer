---
id: pr-readonly
title: "Свойство только для чтения"
order: 4
version: "1.0.0"
---

# Свойство только для чтения

Если у `@property` **нет сеттера**, присвоить значение нельзя: Python бросит `AttributeError`. Так защищают то, что менять не должны: номер заказа, имя владельца, вычисляемую сумму.

```python
class Order:
    def __init__(self, number):
        self._number = number
        self._items = 0

    @property
    def number(self):                 # только чтение
        return self._number

    @property
    def items(self):
        return self._items

    def add_item(self):               # менять состояние можно только методами
        self._items = self._items + 1
```

Менять состояние такого объекта положено **методами**: `order.add_item()`. Прямая запись `order.items = 5` невозможна, и именно это нам и нужно.

Текст самой ошибки зависит от версии Python, поэтому в проверках смотрят на её **тип**: `AttributeError`.

## Трассировка

```python
o = Order(7)               # 1
o.add_item()               # 2
a = o.items                # 3
o.number = 8               # 4  AttributeError
b = o.number               # 5
```

| После строки | `o._number` | `o._items` | Что получилось |
|---|---|---|---|
| 1 | `7` | `0` | |
| 2 | `7` | `1` | метод изменил `_items` |
| 3 | `7` | `1` | `a` равно `1` |
| 4 | `7` | `1` | записи нет: у `number` нет сеттера |
| 5 | `7` | `1` | `b` равно `7` |

## Частые ошибки

Записать значение в `__init__` через имя свойства без сеттера:

```python
def __init__(self, number):
    self.number = number        # неверно: AttributeError уже при создании объекта
```

```python
def __init__(self, number):
    self._number = number       # верно: пишем в «склад»
```

Объект не создаётся вообще, потому что `self.number = ...` — это присваивание свойству, у которого нет сеттера.

## Проверь себя

```python
class Card:
    def __init__(self, owner):
        self._owner = owner

    @property
    def owner(self):
        return self._owner

c = Card("Аня")
try:
    c.owner = "Боря"
except AttributeError:
    r = "запрет"
else:
    r = "записали"
x = c.owner
```

1. Что лежит в `r` и в `x`?
2. Как поменять владельца карты, если это всё-таки разрешено правилами?

<details><summary>Ответ</summary>

1. `r` равно `"запрет"`, `x` равно `"Аня"`.
2. Дописать в класс метод (например, `transfer(new_owner)`) со своими проверками. Или добавить сеттер, если менять владельца можно свободно.

</details>
