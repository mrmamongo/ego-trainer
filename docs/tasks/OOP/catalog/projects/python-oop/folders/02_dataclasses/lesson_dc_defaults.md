---
id: dc-defaults
title: "Значения по умолчанию и default_factory"
order: 2
version: "1.0.0"
---

# Значения по умолчанию и default_factory

У поля dataclass может быть значение по умолчанию, как у параметра функции. Если при создании его не передали, берётся оно:

```python
@dataclass
class OrderLine:
    product: str
    price: int
    count: int = 1
```

```python
a = OrderLine("Чай", 50)          # 1
b = OrderLine("Кофе", 120, 3)     # 2
c = OrderLine("Сок", 80, count=2) # 3
```

| Строка | product | price | count |
|---|---|---|---|
| 1 | `"Чай"` | `50` | `1` (по умолчанию) |
| 2 | `"Кофе"` | `120` | `3` |
| 3 | `"Сок"` | `80` | `2` (назвали аргумент) |

Как и в функциях (`fd-defaults`), поля **без** значения идут первыми, поля со значением после них. Иначе Python откажется создавать класс.

## Ловушка: список по умолчанию

Помнишь, что значение по умолчанию создаётся один раз и общее для всех вызовов? Для списка в обычной функции это тихая ошибка. Dataclass защищает от неё громко: он не даст написать изменяемое значение прямо в поле.

```python
@dataclass
class Quest:
    title: str
    tags: list = []        # неверно: ValueError при создании класса
```

Python остановится сразу и подскажет: нужен `default_factory`. Это **функция**, которую dataclass вызывает для **каждого** нового объекта, чтобы получить свежий список:

```python
from dataclasses import dataclass, field

@dataclass
class Quest:
    title: str
    tags: list = field(default_factory=list)
```

```python
a = Quest("Волки")                # 1
b = Quest("Лис")                  # 2
a.tags.append("бой")              # 3
```

| После строки | `a.tags` | `b.tags` |
|---|---|---|
| 1 | `[]` | не создан |
| 2 | `[]` | `[]` (свой, новый) |
| 3 | `["бой"]` | `[]` (не затронут) |

Так же поступают со словарём (`field(default_factory=dict)`) и множеством (`default_factory=set`).

## Частые ошибки

Вызвать функцию вместо передачи:

```python
tags: list = field(default_factory=list())   # неверно: передали готовый пустой список
```

```python
tags: list = field(default_factory=list)     # верно: передали саму функцию list
```

Забыть импорт: `field` берут из того же модуля, `from dataclasses import dataclass, field`.

## Проверь себя

```python
@dataclass
class Message:
    author: str
    text: str = ""
    likes: int = 0
```

1. Что равно `Message("Аня").text`?
2. Можно ли переставить поля так: `likes: int = 0`, а после него `author: str`?
3. Как правильно задать полю `reactions` пустой список по умолчанию?

<details><summary>Ответ</summary>

1. Пустая строка `""`.
2. Нельзя: поле без значения не может идти после поля со значением.
3. `reactions: list = field(default_factory=list)`.

</details>
