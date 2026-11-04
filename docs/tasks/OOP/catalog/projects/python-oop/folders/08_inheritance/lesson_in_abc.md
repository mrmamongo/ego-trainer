---
id: in-abc
title: "Абстрактный класс: ABC и abstractmethod"
order: 6
version: "1.0.0"
---

# Абстрактный класс: `ABC` и `abstractmethod`

Иногда родитель нужен только как шаблон: «у любого наследника должны быть такие методы», а сам делать их не умеет. Объект такого родителя бессмыслен. Для этого есть `abc`:

```python
from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

    def describe(self):
        return "площадь " + str(self.area())


class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side * self.side
```

| Выражение | Результат |
|---|---|
| `Shape()` | `TypeError`: нельзя создать объект абстрактного класса |
| `Square(3)` | объект создан |
| `Square(3).describe()` | `"площадь 9"`: обычный метод родителя использует `area` наследника |

Правило: класс считается абстрактным, пока у него остался хоть один непереписанный `@abstractmethod`. Наследник, который переписал не все, тоже нельзя создать.

Обычные методы в абстрактном классе остаются и работают, как раньше. Текст `TypeError` зависит от версии Python, поэтому в проверках смотрят на тип ошибки, а не на сообщение.

## Частые ошибки

Забыть `ABC` у класса: `@abstractmethod` тогда ничего не запрещает.

```python
class Shape:                     # неверно: объект создаётся без ошибки
    @abstractmethod
    def area(self): ...
```

```python
class Shape(ABC):                # верно
    @abstractmethod
    def area(self): ...
```

## Проверь себя

```python
class Base(ABC):
    @abstractmethod
    def one(self): ...

    @abstractmethod
    def two(self): ...


class Child(Base):
    def one(self):
        return 1
```

Можно ли создать `Child()`? Что нужно добавить?

<details><summary>Ответ</summary>

Нельзя: метод `two` остался абстрактным, будет `TypeError`. Нужно написать `two` в `Child`.

</details>
