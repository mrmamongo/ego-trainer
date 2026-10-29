---
id: ns-paths
title: "Путь во вложенном словаре"
order: 3
version: "1.0.0"
---

# Путь во вложенном словаре

Чтобы достать значение из вложенного словаря, ты пишешь цепочку ключей: `data["profile"]["settings"]["lang"]`. Те же ключи можно хранить **списком**: это и есть **путь**.

```python
path = ["profile", "settings", "lang"]
```

Путь это данные, поэтому его можно передать функции, сохранить, склеить в строку `"profile.settings.lang"` (`".".join(path)`) и обойти циклом.

## Достать по пути

Идём по ключам и на каждом шаге заменяем «текущее» на то, что лежит глубже:

```python
def get_path(data, path, default):
    current = data
    for key in path:
        if type(current) is not dict or key not in current:
            return default            # дальше идти некуда
        current = current[key]
    return current
```

Пример: `data = {"profile": {"settings": {"lang": "ru"}, "age": 30}}`.

| Путь | Что происходит | Ответ |
|---|---|---|
| `["profile", "settings", "lang"]` | три шага вниз | `"ru"` |
| `["profile", "theme"]` | на втором шаге нет ключа `"theme"` | `default` |
| `["profile", "age", "x"]` | после `"age"` в руках число `30`, а не словарь | `default` |
| `[]` | шагов нет | сам `data` |

## Два способа упереться

1. **Нет ключа**: `key not in current`.
2. **Не словарь**: в руках число, строка, список или `None`. Взять у них ключ нельзя: `30["x"]` упадёт с `TypeError`. Поэтому сначала проверяем `type(current) is not dict`, а потом ключ.

Порядок условий важен: `type(current) is not dict or key not in current`. Если первая часть верна, вторая даже не вычисляется (как в `and`/`or` из первых папок).

## Значение `None` не равно «нет значения»

```python
get_path({"a": None}, ["a"], "нет")     # None: ключ есть, значение None
get_path({}, ["a"], "нет")              # "нет": ключа нет
```

Не пиши `if current[key]:` или `if value is None: return default`. Решает только `key in current`.

## Частые ошибки

```python
current = data[path[0]][path[1]]     # неверно: путь фиксированной длины
```

Цикл по `path` работает с любой длиной. Ещё одна ошибка: вернуть `default` только когда нет ключа, а про «не словарь» забыть: функция упадёт на пути через число.

## Проверь себя

```python
data = {"a": {"b": 0}, "c": "text"}
```

1. Что вернёт `get_path(data, ["a", "b"], 99)`?
2. Что вернёт `get_path(data, ["c", "d"], 99)`?

<details><summary>Ответ</summary>

1. `0`: ключ есть, значение пусть и ложное.
2. `99`: `"text"` не словарь, дальше идти нельзя.

</details>
