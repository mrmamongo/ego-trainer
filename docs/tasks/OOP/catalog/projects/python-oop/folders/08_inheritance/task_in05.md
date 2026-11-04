---
id: IN05
title: "Кто чей наследник"
version: "1.0.0"
level: easy
tags: [inheritance, trace, isinstance]
breaking: false
theory: [in-isinstance, in-basics]
---

# Задача IN05: Кто чей наследник

## Условие

### Как это работает

`isinstance(obj, Класс)` отвечает «этот объект создан из `Класса` **или из его наследника**?». `issubclass(Дочерний, Родитель)` сравнивает два класса. Оба возвращают `True` или `False`.

```python
class Tool: pass                  # 1
class Axe(Tool): pass             # 2
class Hammer(Tool): pass          # 3
a = Axe()                         # 4
```

| Выражение | Результат | Почему |
|---|---|---|
| `isinstance(a, Axe)` | `True` | объект создан из `Axe` |
| `isinstance(a, Tool)` | `True` | `Axe` — наследник `Tool` |
| `isinstance(a, Hammer)` | `False` | это соседний класс |
| `issubclass(Axe, Tool)` | `True` | наследник относится к родителю |
| `issubclass(Tool, Axe)` | `False` | наоборот не работает |
| `type(a) == Tool` | `False` | `type` точный и родителей не считает |

### Задание

Есть небольшая иерархия юнитов. Ответь на вопросы про объект паладина.

## Правила

- Меняй только строчки с `None`.
- Строки `def task_in05_isinstance():` и `return ...` самой рамки не трогай: так проверка читает твои ответы.

## Учебные цели

- Различать `isinstance` и `issubclass`.
- Понимать, что `isinstance` учитывает родителей, а `type(x) == Класс` — нет.

## Проверка понимания

Почему `isinstance(p, Unit)` тоже было бы `True`? Чем `type(p) == Warrior` отличается от `isinstance(p, Warrior)`?
