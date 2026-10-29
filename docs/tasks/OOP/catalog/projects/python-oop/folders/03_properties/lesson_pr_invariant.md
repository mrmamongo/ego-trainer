---
id: pr-invariant
title: "Объект всегда корректен"
order: 5
version: "1.0.0"
---

# Объект всегда корректен

**Инвариант** — правило, которое верно для объекта всегда: «баланс не меньше нуля», «hp от 0 до максимума», «в email есть `@`». Хороший класс не даёт нарушить такое правило ни при создании, ни потом.

Для этого проверка записывается **в одном месте** — в сеттере, а `__init__` присваивает через свойство, а не через `_поле`:

```python
class Account:
    def __init__(self, owner, balance):
        self.owner = owner
        self.balance = balance          # через свойство: сеттер проверит

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError("баланс не может быть отрицательным")
        self._balance = value

    def deposit(self, amount):
        self.balance = self.balance + amount

    def withdraw(self, amount):
        self.balance = self.balance - amount
```

Теперь `Account("Аня", -5)` бросит `ValueError` ещё при создании, а `withdraw` получает проверку «даром»: он тоже пишет через свойство. Не нужно копировать `if` в каждый метод.

## Трассировка

```python
a = Account("Аня", 100)     # 1
a.withdraw(30)              # 2
a.withdraw(500)             # 3  ValueError
x = a.balance               # 4
```

| После строки | `a._balance` | Что получилось |
|---|---|---|
| 1 | `100` | `__init__` прошёл через сеттер |
| 2 | `70` | новое значение `70` проверено сеттером |
| 3 | `70` | сеттер увидел `-430` и бросил `ValueError` |
| 4 | `70` | `x` равно `70` |

## Частые ошибки

Записать в `__init__` прямо в `_balance`:

```python
def __init__(self, owner, balance):
    self._balance = balance          # неверно: Account("Аня", -5) создастся
```

```python
def __init__(self, owner, balance):
    self.balance = balance           # верно: проверка сработает и при создании
```

Размножать проверку по методам: в пятом месте её забудут, и правило сломано. Одно место в сеттере решает эту проблему.

## Проверь себя

```python
class Meter:
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        if v < 0:
            raise ValueError("меньше нуля")
        self._value = v

m = Meter(5)
m.value = m.value + 3
x = m.value
```

1. Чему равен `x`?
2. Что произойдёт при `Meter(-1)`?

<details><summary>Ответ</summary>

1. `8`.
2. `ValueError("меньше нуля")`: `__init__` присваивает `self.value`, то есть идёт через сеттер, а сеттер отклоняет `-1`. Объект не создаётся.

</details>
