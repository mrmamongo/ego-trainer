---
id: pt-json
title: "Сохранить и загрузить объект: JSON и io.StringIO"
order: 6
version: "1.0.0"
---

# Сохранить и загрузить объект: JSON и `io.StringIO`

Объект нельзя записать в файл как есть. Путь такой: объект → словарь (`to_dict`) → текст JSON (`json.dumps`) → файл, а обратно: файл → текст → словарь (`json.loads`) → объект (`from_dict`).

```python
import json

class Profile:
    def __init__(self, name, level):
        self.name = name
        self.level = level

    def to_dict(self):
        return {"name": self.name, "level": self.level}

def profile_from_dict(data):
    return Profile(data["name"], data["level"])

text = json.dumps(Profile("Аня", 3).to_dict(), ensure_ascii=False)    # 1
data = json.loads(text)                                               # 2
p = profile_from_dict(data)                                           # 3
```

| После строки | Значение |
|---|---|
| 1 | `text` равно `'{"name": "Аня", "level": 3}'`: это строка |
| 2 | `data` равно `{"name": "Аня", "level": 3}`: снова словарь |
| 3 | `p.name` равно `"Аня"`, `p.level` равно `3` |

`ensure_ascii=False` оставляет русские буквы читаемыми, а не `А...`. JSON знает только числа, строки, `True/False` (в тексте `true/false`), `None` (в тексте `null`), списки и словари. Сложные объекты внутри `to_dict` надо свести к этим типам.

## Файл без диска

Запись и чтение идут через **файлоподобный объект**. Настоящий файл (`open`) и `io.StringIO` работают одинаково:

```python
import io

file = io.StringIO()
file.write(text)             # записали
file.seek(0)                 # вернулись в начало, как после повторного open
back = file.read()           # прочитали всё как строку
```

`file.getvalue()` у `StringIO` отдаёт всё записанное разом. Функции `save(profile, file)` и `load(file)` принимают файл параметром и не знают, какой он. Поэтому в проверке подходит `StringIO`, а в жизни `open("save.json", "w")`.

## Частые ошибки

Забыть `seek(0)` перед чтением: указатель стоит в конце, `read()` вернёт пустую строку, а `json.loads("")` упадёт. И `json.dumps(profile)` без `to_dict`: объект JSON не знает, будет `TypeError`.

## Проверь себя

```python
file = io.StringIO()
file.write(json.dumps({"hp": 5}))
file.seek(0)
data = json.loads(file.read())
```

1. Чему равен `data["hp"]`?
2. Что вернёт `file.read()` ещё раз сразу после этого?

<details><summary>Ответ</summary>

1. `5`.
2. Пустую строку `""`: указатель уже в конце.

</details>
