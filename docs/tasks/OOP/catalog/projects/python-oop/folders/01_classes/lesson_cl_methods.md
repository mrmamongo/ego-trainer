---
id: cl-methods
title: "Методы: изменить или вернуть"
order: 3
version: "1.0.0"
---

# Методы: изменить или вернуть

**Метод** — функция внутри класса. Его вызывают через объект: `hero.hit(10)`, а в самом методе объект доступен как `self`.

Методы бывают двух видов. Ты уже знаешь их разницу по `print` и `return`.

- **Команда** меняет состояние: `self.hp = self.hp - damage`. Обычно ничего не возвращает, значит, наружу выходит `None`.
- **Вопрос** считает ответ и возвращает его через `return`. Объект остаётся прежним.

```python
class Player:
    def __init__(self, hp):
        self.hp = hp

    def hit(self, damage):               # команда
        self.hp = self.hp - damage

    def is_alive(self):                  # вопрос
        return self.hp > 0

    def hit_and_check(self, damage):     # и то и другое
        self.hit(damage)
        return self.is_alive()
```

Метод может вызвать другой метод **того же объекта**, но только через `self.`: `self.hit(damage)`. Без `self.` Python не найдёт имя.

```python
p = Player(10)                 # 1
p.hit(4)                       # 2
a = p.is_alive()               # 3
b = p.hit_and_check(6)         # 4
```

| После строки | p.hp | Что получилось |
|---|---|---|
| 1 | `10` | |
| 2 | `6` | `hit` изменил состояние, вернул `None` |
| 3 | `6` | `a` равно `True`, состояние не менялось |
| 4 | `0` | `b` равно `False`: `hit` сработал, потом `is_alive` ответил про `0 > 0` |

## Частые ошибки

Посчитать новое значение, но не записать его в объект:

```python
def heal(self, amount):
    return self.hp + amount          # неверно: объект остался прежним
```

```python
def heal(self, amount):
    self.hp = self.hp + amount       # верно: состояние обновлено
```

Вызвать свой метод без `self.`: `is_alive()` даст `NameError`. Нужно `self.is_alive()`.

## Проверь себя

```python
class Counter:
    def __init__(self):
        self.n = 0

    def inc(self):
        self.n = self.n + 1

    def double(self):
        return self.n * 2

c = Counter()
c.inc()
c.inc()
x = c.double()
y = c.inc()
```

1. Чему равны `c.n` и `x` в конце?
2. Что лежит в `y`?

<details><summary>Ответ</summary>

1. `c.n` равно `3` (после третьего `inc`), а `x` равно `4`: он посчитан, когда `n` было `2`.
2. `None`: `inc` ничего не возвращает.

</details>
