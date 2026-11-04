---
id: in-isinstance
title: "isinstance и issubclass"
order: 5
version: "1.0.0"
---

# `isinstance` и `issubclass`

`isinstance(obj, Класс)` отвечает на вопрос: «объект создан из этого класса **или из его наследника**?». `issubclass(Дочерний, Родитель)` спрашивает то же про два класса.

```python
class Unit: pass
class Warrior(Unit): pass
class Mage(Unit): pass

w = Warrior()
```

| Выражение | Результат | Почему |
|---|---|---|
| `isinstance(w, Warrior)` | `True` | объект создан из `Warrior` |
| `isinstance(w, Unit)` | `True` | `Warrior` — наследник `Unit` |
| `isinstance(w, Mage)` | `False` | соседний класс |
| `issubclass(Warrior, Unit)` | `True` | класс против класса |
| `issubclass(Unit, Warrior)` | `False` | наоборот не работает |
| `type(w) == Unit` | `False` | `type` точный, родителей не учитывает |

## Когда не стоит

`isinstance` удобен в проверках входных данных. Но если ты пишешь цепочку

```python
if isinstance(unit, Warrior):
    ...
elif isinstance(unit, Mage):
    ...
```

то обычно лучше добавить в классы общий метод (см. карточку про полиморфизм). Тогда новый вид юнита не придётся вписывать в каждую такую цепочку.

## Частые ошибки

Сравнивать `type(x) == Класс`: наследники такой проверки не пройдут.

```python
if type(unit) == Unit:           # неверно: Warrior не пройдёт
    ...
```

```python
if isinstance(unit, Unit):       # верно: сюда попадают и Warrior, и Mage
    ...
```

## Проверь себя

```python
class A: pass
class B(A): pass
class C(B): pass

c = C()
```

Чему равны `isinstance(c, A)`, `isinstance(A(), C)` и `issubclass(C, A)`?

<details><summary>Ответ</summary>

`True`, `False`, `True`. Цепочка `C` → `B` → `A` считается: `c` относится и к `B`, и к `A`. А родитель не является экземпляром наследника.

</details>
