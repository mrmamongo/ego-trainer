---
id: dc-frozen
title: "frozen: запись, которую нельзя менять"
order: 4
version: "1.0.0"
---

# `frozen`: запись, которую нельзя менять

Бывает, что запись описывает факт, и править её задним числом нельзя: строка заказа, результат матча, снимок профиля на дату. Тогда пишут `frozen=True`:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Profile:
    name: str
    level: int = 1
```

После этого поля можно **только читать**. Любая попытка записи бросает `FrozenInstanceError`:

```python
p = Profile("Аня")
p.level = 5        # FrozenInstanceError: cannot assign to field 'level'
```

Зачем это нужно: никто «случайно» не изменит запись по другому имени (помнишь, два имени одного объекта?), и по ней всегда можно доверять тому, что она была создана такой.

## Изменить = сделать новую запись

Если значение всё же поменялось, делают **новую** запись с одним другим полем. Для этого есть `dataclasses.replace`:

```python
from dataclasses import replace

p = Profile("Аня")                      # 1
q = replace(p, level=p.level + 1)       # 2
```

| После строки | p | q |
|---|---|---|
| 1 | `Profile(name='Аня', level=1)` | не создана |
| 2 | `Profile(name='Аня', level=1)` (не изменилась) | `Profile(name='Аня', level=2)` |

`replace` берёт старую запись, копирует поля и подставляет те, что ты назвал. Старая запись остаётся как была.

С dict-записями ты делал похоже: `new = dict(old)`, потом `new["level"] = 2`. Здесь копирование и замена сделаны одним вызовом.

## Частые ошибки

Выбросить результат `replace`:

```python
replace(p, level=2)          # неверно: новая запись нигде не сохранена, p не изменилась
```

```python
p = replace(p, level=2)      # верно: имя `p` теперь указывает на новую запись
```

Менять поле у frozen-записи: `p.level = p.level + 1` упадёт. Нужно `p = replace(p, level=p.level + 1)`.

## Проверь себя

```python
p = Profile("Боря", 3)
q = replace(p, name="Вика")
```

1. Чему равны `p.name` и `q.name`?
2. Чему равно `q.level`?
3. Что случится при `q.level = 9`?

<details><summary>Ответ</summary>

1. `"Боря"` и `"Вика"`.
2. `3`: поле, которое не назвали, копируется из `p`.
3. Ошибка `FrozenInstanceError`.

</details>
