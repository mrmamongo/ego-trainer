---
id: pt-with
title: "with: __enter__, __exit__ и contextmanager"
order: 5
version: "1.0.0"
---

# `with`: `__enter__`, `__exit__` и `contextmanager`

`with` гарантирует, что «уборка» выполнится, даже если внутри блока случилась ошибка. Так закрывают файлы, а в банке откатывают операцию. Объекту нужны два метода:

- `__enter__(self)` запускается при входе; то, что он вернёт, попадает в `as`;
- `__exit__(self, exc_type, exc, tb)` запускается при выходе **всегда**. Если в блоке была ошибка, `exc_type` — её класс, иначе `None`.

Возвращаемое значение `__exit__` решает судьбу ошибки:

| `__exit__` вернул | Что с ошибкой из блока |
|---|---|
| `False` или `None` | ошибка идёт дальше, её можно поймать снаружи через `try` |
| `True` | ошибка **подавлена**, программа продолжает после `with` |

```python
events = []

class Guard:
    def __init__(self, hide):
        self.hide = hide
    def __enter__(self):
        events.append("вход")
        return self
    def __exit__(self, exc_type, exc, tb):
        events.append("выход")
        return self.hide

with Guard(True):                       # 1
    raise ValueError("x")
events.append("после")                  # 2
```

| После строки | `events` |
|---|---|
| 1 | `["вход", "выход"]`: `__exit__` вернул `True`, ошибка проглочена |
| 2 | `["вход", "выход", "после"]` |

С `Guard(False)` строка 2 не выполнилась бы: `ValueError` вылетел бы из `with`.

## Откат при ошибке

```python
class Transaction:
    def __init__(self, wallet):
        self.wallet = wallet
    def __enter__(self):
        self.saved = self.wallet.balance
        return self.wallet
    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:
            self.wallet.balance = self.saved       # вернули как было
        return False                               # ошибку не прячем
```

## Короче: `contextlib.contextmanager`

Генератор с одним `yield` тоже может быть менеджером контекста: всё до `yield` — вход, после — выход.

```python
from contextlib import contextmanager

@contextmanager
def transaction(wallet):
    saved = wallet.balance
    try:
        yield wallet
    except Exception:
        wallet.balance = saved
        raise                  # пробросить ошибку дальше
```

Если уборка нужна и при успехе, и при ошибке, ставь её в `finally`. Голый `raise` в `except` пробрасывает ошибку дальше; без него она была бы съедена.

## Частые ошибки

`return True` в `__exit__` «на всякий случай»: все ошибки пропадают молча, и баг не найти. Возвращай `False`, а `True` только когда хочешь подавить ошибку намеренно.

## Проверь себя

Что окажется в `events`, если в примере с `Guard(False)` блок `with` стоит внутри `try ... except ValueError: events.append("поймано")`?

<details><summary>Ответ</summary>

`["вход", "выход", "поймано"]`: `__exit__` отработал, ошибка вылетела наружу, и её поймал `except`.

</details>
