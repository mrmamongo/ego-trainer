# Задача D3: Проваленные билды и их длительность

**Блок:** D — Разные домены
**Сложность:** medium
**Темы:** CI/CD, фильтрация, проекция словарей

## Условие

Функция отбирает из списка билдов те, что завершились провалом (`status == "failed"`), и формирует по каждому компактный отчёт с идентификатором билда, длительностью и веткой. Поле `status` в результат не включается.

## Аргументы

- `builds` — список словарей: `[{"build_id": "B1", "status": "failed", "duration_sec": 45, "branch": "main"}, ...]`

## Возвращает

Список словарей ТОЛЬКО для `status == "failed"`, каждый с ключами: `{"build_id": "...", "duration_sec": N, "branch": "..."}` (ключ `"status"` убрать).

## Правила

- В результат попадают только билды со `status == "failed"`.
- В каждом словаре результата остаются только ключи `build_id`, `duration_sec`, `branch`.
- Ключ `status` удаляется из выходных словарей.

## Пример

```python
>>> builds = [
...     {"build_id": "B1", "status": "success", "duration_sec": 120, "branch": "main"},
...     {"build_id": "B2", "status": "failed", "duration_sec": 45, "branch": "feature/auth"},
...     {"build_id": "B3", "status": "success", "duration_sec": 90, "branch": "main"},
...     {"build_id": "B4", "status": "failed", "duration_sec": 12, "branch": "hotfix/db"},
...     {"build_id": "B5", "status": "failed", "duration_sec": 200, "branch": "feature/ui"},
... ]
>>> task_d3_failed_builds(builds)
[
    {"build_id": "B2", "duration_sec": 45, "branch": "feature/auth"},
    {"build_id": "B4", "duration_sec": 12, "branch": "hotfix/db"},
    {"build_id": "B5", "duration_sec": 200, "branch": "feature/ui"},
]
```

<details>
<summary>Эталонное решение</summary>

```python
def task_d3_failed_builds(builds):
    return [
        {"build_id": b["build_id"], "duration_sec": b["duration_sec"], "branch": b["branch"]}
        for b in builds if b["status"] == "failed"
    ]
```

</details>
