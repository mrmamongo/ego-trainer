---
id: pr-setter
title: "Сеттер: присваивание с проверкой"
order: 3
version: "1.0.0"
---

# Сеттер: присваивание с проверкой

Свойство можно не только читать, но и **записывать**: `player.hp = 20`. Для записи пишут второй метод с тем же именем и декоратором `@имя.setter`. В нём живёт проверка, и при недопустимом значении он бросает `ValueError`.

Само значение хранят во «внутреннем» поле с подчёркиванием: `_hp`. Свойство `hp` — это вход, а `_hp` — склад.

```python
class Player:
    def __init__(self, hp):
        self._hp = hp

    @property
    def hp(self):                    # читаем: p.hp
        return self._hp

    @hp.setter
    def hp(self, value):             # пишем: p.hp = 5
        if value < 0:
            raise ValueError("hp не может быть отрицательным")
        self._hp = value
```

Порядок важен: сначала `@property`, потом `@hp.setter`, имена методов одинаковые. Снаружи ничего не поменялось: `p.hp` и `p.hp = 5`, только теперь запись проходит через проверку.

## Трассировка

```python
p = Player(10)         # 1
p.hp = 4               # 2
p.hp = -3              # 3  ValueError
x = p.hp               # 4
```

| После строки | `p._hp` | Что получилось |
|---|---|---|
| 1 | `10` | |
| 2 | `4` | сеттер проверил `4` и записал |
| 3 | `4` | сеттер бросил `ValueError`, `_hp` не тронут |
| 4 | `4` | `x` равно `4` |

Ошибка обрывает присваивание, поэтому старое значение остаётся.

## Частые ошибки

Записывать в сеттере в само свойство:

```python
@hp.setter
def hp(self, value):
    self.hp = value            # неверно: это снова вызов сеттера, бесконечно
```

```python
@hp.setter
def hp(self, value):
    self._hp = value           # верно: пишем в «склад»
```

Первый вариант заканчивается `RecursionError`: сеттер вызывает сам себя, пока Python не остановит рекурсию. Правило простое: внутри свойства работаем с `_hp`, снаружи — с `hp`.

## Проверь себя

```python
class Box:
    def __init__(self):
        self._size = 1

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        if value <= 0:
            raise ValueError("размер должен быть больше нуля")
        self._size = value

b = Box()
b.size = 5
try:
    b.size = 0
except ValueError:
    pass
x = b.size
```

1. Чему равен `x`?
2. Почему в сеттере написано `self._size = value`, а не `self.size = value`?

<details><summary>Ответ</summary>

1. `5`: вторая запись отклонена, значение осталось прежним.
2. `self.size = value` снова вызвал бы сеттер, и он бесконечно вызывал бы сам себя (`RecursionError`). Хранить нужно в `_size`.

</details>
