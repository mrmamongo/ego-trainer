---
id: pr-property
title: "@property: значение без скобок"
order: 2
version: "1.0.0"
---

# `@property`: значение без скобок

Бывает, что данные можно **вычислить** из других. Градусы по Фаренгейту считаются из градусов Цельсия. Хранить оба числа не нужно: одно обязательно устареет, когда поменяют другое.

Декоратор `@property` превращает метод в **свойство**: его читают как обычный атрибут, без круглых скобок, а считается оно каждый раз заново.

```python
class Temperature:
    def __init__(self, celsius):
        self._celsius = celsius

    def warm(self, degrees):
        self._celsius = self._celsius + degrees

    @property
    def fahrenheit(self):
        return self._celsius * 9 / 5 + 32

t = Temperature(100)
t.fahrenheit            # 212.0  — без скобок!
```

Снаружи это выглядит как поле (`t.fahrenheit`), а внутри это маленькая функция. Поэтому значение всегда свежее.

## Трассировка

```python
t = Temperature(0)        # 1
a = t.fahrenheit          # 2
t.warm(10)                # 3
b = t.fahrenheit          # 4
```

| После строки | `t._celsius` | Что получилось |
|---|---|---|
| 1 | `0` | |
| 2 | `0` | `a` равно `32.0` |
| 3 | `10` | |
| 4 | `10` | `b` равно `50.0`: свойство посчитано заново |

## Частые ошибки

Вызывать свойство как функцию:

```python
t.fahrenheit()          # неверно: TypeError, число нельзя «вызвать»
```

```python
t.fahrenheit            # верно: свойство читают без скобок
```

Считать значение один раз в `__init__` и хранить копией:

```python
self.fahrenheit = celsius * 9 / 5 + 32     # неверно: после warm() устареет
```

```python
@property
def fahrenheit(self): ...                  # верно: считается при каждом чтении
```

## Проверь себя

```python
class Order:
    def __init__(self, price, count):
        self._price = price
        self._count = count

    @property
    def total(self):
        return self._price * self._count

o = Order(5, 3)
x = o.total
```

1. Чему равен `x`?
2. Что произойдёт при `o.total()`?

<details><summary>Ответ</summary>

1. `15`.
2. `TypeError`: `o.total` уже число `15`, а число вызвать нельзя. Скобки не нужны.

</details>
