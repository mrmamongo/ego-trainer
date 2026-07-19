# Задача F1: Найди первый критический баг

**Блок:** F — Базовые паттерны
**Сложность:** easy
**Темы:** find, linear search, first match

## Условие

В баг-трекере нужно быстро найти первый критический баг в списке.
Функция перебирает список багов и возвращает заголовок первого, у которого `severity == "critical"`.

## Аргументы

- `bugs` — список словарей вида `[{"id": "B1", "severity": "critical", "title": "Crash on login"}, ...]`

## Возвращает

Строку — значение поля `"title"` первого бага с `severity == "critical"`.
Если такого бага нет — пустую строку `""`.

## Правила

- Верни значение поля `"title"` первого бага с `severity == "critical"`.
- Если критического бага нет — верни пустую строку `""`.

## Пример

```python
bugs = [
    {"id": "B1", "severity": "minor", "title": "Typo in footer"},
    {"id": "B2", "severity": "major", "title": "Slow loading"},
    {"id": "B3", "severity": "critical", "title": "Crash on login"},
    {"id": "B4", "severity": "minor", "title": "Wrong icon"},
]

task_f1_find_critical(bugs)
# -> "Crash on login"
```

<details>
<summary>Эталонное решение</summary>

```python
def task_f1_find_critical(bugs):
    for b in bugs:
        if b["severity"] == "critical":
            return b["title"]
    return ""
```

</details>
