# Задача F3: Сколько задач в статусе "pending"

**Блок:** F — Базовые паттерны
**Сложность:** easy
**Темы:** count, filter

## Условие

Таск-трекер хранит список задач со статусами.
Функция подсчитывает, сколько задач находятся в статусе `"pending"`.

## Аргументы

- `tasks` — список словарей вида `[{"id": "T1", "status": "pending"}, ...]`

## Возвращает

Число — количество записей, у которых `status == "pending"`.

## Правила

- Верни число — сколько записей с `status == "pending"`.

## Пример

```python
tasks = [
    {"id": "T1", "status": "done"},
    {"id": "T2", "status": "pending"},
    {"id": "T3", "status": "in_progress"},
    {"id": "T4", "status": "pending"},
    {"id": "T5", "status": "pending"},
    {"id": "T6", "status": "done"},
]

task_f3_count_pending(tasks)
# -> 3
```

<details>
<summary>Эталонное решение</summary>

```python
def task_f3_count_pending(tasks):
    count = 0
    for t in tasks:
        if t["status"] == "pending":
            count += 1
    return count
```

</details>
