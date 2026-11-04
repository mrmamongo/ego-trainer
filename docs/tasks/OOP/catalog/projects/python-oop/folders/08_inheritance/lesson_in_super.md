---
id: in-super
title: "super(): позвать родителя"
order: 3
version: "1.0.0"
---

# `super()`: позвать родителя

Переопределённый метод заменяет родительский целиком. Но часто нужно **добавить** к работе родителя, а не выбросить её. Тогда внутри метода зовут `super().метод(...)`: это версия родителя.

Самый частый случай — `__init__`. Если у наследника появляются свои поля, он пишет свой `__init__`, а общую часть отдаёт родителю:

```python
class Unit:
    def __init__(self, name, hp):
        self.name = name
        self.hp = hp

    def describe(self):
        return self.name + ":" + str(self.hp)


class Mage(Unit):
    def __init__(self, name, hp, mana):
        super().__init__(name, hp)       # родитель кладёт name и hp
        self.mana = mana                 # маг кладёт своё

    def describe(self):
        return super().describe() + "/" + str(self.mana)


m = Mage("Мерлин", 30, 50)               # 1
a = m.describe()                         # 2
```

| Шаг | Что происходит |
|---|---|
| 1 | `Mage.__init__` вызывает `Unit.__init__`: появляются `name` и `hp`, затем `mana` |
| 2 | `Mage.describe` берёт строку у `Unit.describe` (`"Мерлин:30"`) и дописывает `"/50"` |

Итог `a`: `"Мерлин:30/50"`. Если правило подсчёта поменяется у родителя, маг подхватит это сам.

## Частые ошибки

Свой `__init__` без вызова родителя: его поля не появятся.

```python
class Mage(Unit):
    def __init__(self, name, hp, mana):
        self.mana = mana                  # неверно: name и hp не записаны
```

```python
class Mage(Unit):
    def __init__(self, name, hp, mana):
        super().__init__(name, hp)        # верно
        self.mana = mana
```

Ещё одна ловушка: вместо `super().describe()` написать `self.describe()`. Метод позовёт сам себя бесконечно.

## Проверь себя

```python
class A:
    def __init__(self, x):
        self.x = x

class B(A):
    def __init__(self, x, y):
        super().__init__(x * 2)
        self.y = y

b = B(3, 4)
```

Чему равны `b.x` и `b.y`?

<details><summary>Ответ</summary>

`b.x` равно `6` (родитель получил `3 * 2`), `b.y` равно `4`.

</details>
