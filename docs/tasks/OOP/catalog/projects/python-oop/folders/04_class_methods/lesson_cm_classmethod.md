---
id: cm-classmethod
title: "@classmethod: создать объект из словаря или строки"
order: 4
version: "1.0.0"
---

# `@classmethod`: создать объект из словаря или строки

Данные снаружи (сохранение игры, строка из файла) приходят словарём или текстом, а объект нужен `Player`. В папке про dataclass ты писал для этого обычную функцию `message_from_dict`. Лучше положить её **внутрь класса**: тогда она всегда рядом с классом, который создаёт. Для этого есть `@classmethod`.

```python
class Player:
    def __init__(self, name, hp):
        self.name = name
        self.hp = hp

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["hp"])

    @classmethod
    def from_string(cls, text):            # "Аня:30"
        name, hp = text.split(":")
        return cls(name, int(hp))
```

Первым параметром у такого метода стоит не `self`, а `cls`: это **сам класс**. Вызывают метод через класс, объект для этого не нужен:

```python
p = Player.from_dict({"name": "Аня", "hp": 30})    # 1
q = Player.from_string("Боря:12")                  # 2
```

| После строки | Что получилось |
|---|---|
| 1 | `p.name` равно `"Аня"`, `p.hp` равно `30` |
| 2 | `q.name` равно `"Боря"`, `q.hp` равно `12`: `int` превратил строку `"12"` в число |

Такие методы называют **альтернативными конструкторами**: `__init__` принимает поля по отдельности, а `from_dict` и `from_string` собирают те же поля из другой формы данных. Словарную запись `{"name": ..., "hp": ...}` из папки про словари теперь можно превратить в `Player` одной строкой.

## Зачем `cls`, а не `Player`

`cls(...)` создаёт объект того класса, у которого вызвали метод. Пока класс один, `cls(...)` и `Player(...)` дают одно и то же. Но когда у класса появятся потомки (папка про наследование), `Child.from_dict(...)` через `cls` создаст `Child`, а через жёстко записанное `Player` создаст `Player`. Поэтому привыкай писать `cls`.

Через `cls` можно и менять атрибут класса: `cls.created = cls.created + 1`.

## Частые ошибки

Забыть `@classmethod`:

```python
def from_dict(cls, data):        # без декоратора
    ...
```

Тогда `Player.from_dict(d)` отдаст словарь в параметр `cls`, а `data` останется без значения: `TypeError`.

Забыть `return`: метод создаст объект и выбросит его, а вызывающий получит `None`.

Написать `self` вместо `cls` в сигнатуре: Python не сообщит об ошибке, но смысл потеряется, ведь объекта у такого метода нет.

## Проверь себя

```python
class Item:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    @classmethod
    def from_string(cls, text):      # "Меч:120"
        name, price = text.split(":")
        return cls(name, int(price))

x = Item.from_string("Меч:120")
y = x.price + 5
```

1. Чему равны `x.name` и `y`?
2. Что вернёт метод, если убрать слово `return`?

<details><summary>Ответ</summary>

1. `"Меч"` и `125`.
2. `None`: объект создаётся, но наружу не возвращается.

</details>
