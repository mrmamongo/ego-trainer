---
id: mo-arith
title: "__add__, __sub__, __mul__: арифметика объектов"
order: 1
version: "1.0.0"
---

# `__add__`, `__sub__`, `__mul__`: арифметика объектов

Числа складываются плюсом, строки тоже. Свой класс Python складывать не умеет: `Money(100) + Money(50)` упадёт с `TypeError`. Научить его можно магическим методом `__add__(self, other)`: Python вызывает его, когда видит `a + b`. Так же `__sub__` отвечает за `a - b`, а `__mul__` за `a * k`.

Главное правило: такой метод **возвращает новый объект** и не меняет ни `self`, ни `other`. Ведь после `c = a + b` ты ждёшь, что `a` и `b` остались прежними, как у чисел.

```python
class Money:
    def __init__(self, kopecks):
        self.kopecks = kopecks

    def __add__(self, other):
        return Money(self.kopecks + other.kopecks)

    def __sub__(self, other):
        return Money(self.kopecks - other.kopecks)

    def __mul__(self, k):
        return Money(self.kopecks * k)

a = Money(100)             # 1
b = Money(30)              # 2
c = a + b                  # 3
d = c - b                  # 4
e = a * 3                  # 5
```

| После строки | Что получилось | Почему |
|---|---|---|
| 3 | `c.kopecks` равно `130`, `c` новый объект | `a + b` позвал `a.__add__(b)` |
| 4 | `d.kopecks` равно `100`, `d is a` равно `False` | равные копейки, но объект другой |
| 5 | `e.kopecks` равно `300`, `a.kopecks` всё ещё `100` | `__mul__` взял число `3` справа |

Справа от `*` стоит обычное число, а не `Money`: умножать деньги на деньги не имеет смысла, а на количество имеет.

## Частые ошибки

Изменить `self` и вернуть его:

```python
def __add__(self, other):
    self.kopecks += other.kopecks      # a тоже изменился!
    return self
```

После `c = a + b` окажется, что `c is a`, а у `a` стало на 30 копеек больше. Такую ошибку трудно заметить: код вроде бы «работает». Правильно: `return Money(self.kopecks + other.kopecks)`.

Вторая ошибка: забыть `return`. Тогда `a + b` даст `None`.

## Проверь себя

```python
p = Money(50)
q = Money(70)
r = p + q
s = r * 2
```

1. Чему равны `r.kopecks` и `s.kopecks`?
2. Чему равно `p.kopecks` после этих строк?
3. Верно ли, что `r is p`?

<details><summary>Ответ</summary>

1. `120` и `240`.
2. `50`: метод создал новый объект и старый не тронул.
3. Нет, `False`: `r` это другой объект.

</details>
