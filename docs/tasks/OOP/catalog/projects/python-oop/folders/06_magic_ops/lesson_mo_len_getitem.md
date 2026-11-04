---
id: mo-len-getitem
title: "__len__ и __getitem__: класс как коллекция"
order: 4
version: "1.0.0"
---

# `__len__` и `__getitem__`: класс как коллекция

Список отвечает на `len(xs)` и на `xs[0]`. Свой класс тоже можно научить: `len(obj)` вызывает `obj.__len__()`, а `obj[key]` вызывает `obj.__getitem__(key)`. Обычно объект хранит внутри список или словарь и передаёт запросы ему.

```python
class Playlist:
    def __init__(self, tracks):
        self.tracks = tracks

    def __len__(self):
        return len(self.tracks)

    def __getitem__(self, index):
        return self.tracks[index]

class Inventory:
    def __init__(self, items):
        self.items = items              # словарь {название: количество}

    def __getitem__(self, name):
        return self.items[name]

p = Playlist(["rock", "jazz", "pop"])     # 1
n = len(p)                                # 2
a = p[0]                                  # 3
b = p[-1]                                 # 4
inv = Inventory({"меч": 1})               # 5
c = inv["меч"]                            # 6
```

| Строка | Результат | Почему |
|---|---|---|
| 2 | `3` | `len(p)` вызвал `p.__len__()` |
| 3 | `"rock"` | `p[0]` вызвал `p.__getitem__(0)` |
| 4 | `"pop"` | отрицательный индекс считает с конца, это делает сам список внутри |
| 6 | `1` | ключ может быть не числом, а строкой: метод получает то, что внутри скобок |

## Ошибки: IndexError и KeyError

Если индекс за пределами, список внутри сам бросит `IndexError`, а словарь для неизвестного ключа `KeyError`. Это правильное поведение: `p[10]` обязан падать, а не возвращать `None`. Если хочешь свой текст, бросай ошибку сам:

```python
def __getitem__(self, index):
    if not -len(self.tracks) <= index < len(self.tracks):
        raise IndexError("нет такого трека")
    return self.tracks[index]
```

## Частые ошибки

Вернуть из `__len__` не число, а список или `None`: `len(obj)` тогда упадёт с `TypeError`.

Спрятать ошибку: `return self.items.get(name)` вместо `self.items[name]`. Тогда неизвестный ключ даст `None`, а не `KeyError`.

Тип ключа и ошибка связаны: для индексов принято `IndexError`, для ключей `KeyError`.

## Проверь себя

```python
p = Playlist(["a", "b"])
```

1. Чему равны `len(p)` и `p[-1]`?
2. Что даст `p[2]`?
3. Какой метод вызовет `Inventory({"меч": 1})["лук"]` и чем всё кончится?

<details><summary>Ответ</summary>

1. `2` и `"b"`.
2. `IndexError`: индекса `2` в списке из двух элементов нет.
3. `__getitem__("лук")`, внутри `KeyError`: такого ключа в словаре нет.

</details>
