# Задача D5: Статистика по endpoint'ам

**Блок:** D — Разные домены
**Сложность:** medium
**Темы:** API Gateway, агрегация, среднее значение, сортировка

## Условие

Функция собирает статистику обращений к API-эндпоинтам: для каждого endpoint подсчитывается количество запросов и среднее время ответа. Результат упорядочивается по алфавиту названий endpoint'ов.

## Аргументы

- `requests` — список словарей: `[{"endpoint": "/api/users", "method": "GET", "status": 200, "ms": 45}, ...]`

## Возвращает

Список словарей (по одному на endpoint):
```
[
    {"endpoint": "/api/users", "count": 50, "avg_ms": 42},
    ...
]
```

- `count` = сколько запросов к endpoint
- `avg_ms` = среднее время ответа, округлённое до целого (`round`)
- Порядок: по алфавиту endpoint.

## Правила

- Группировка по полю `endpoint` (метод и статус не учитываются).
- `count` — количество запросов к данному endpoint.
- `avg_ms` — среднее арифметическое поля `ms`, округлённое до целого через `round`.
- Результат отсортирован по алфавиту endpoint.

## Пример

```python
>>> requests = [
...     {"endpoint": "/api/users", "method": "GET", "status": 200, "ms": 45},
...     {"endpoint": "/api/users", "method": "GET", "status": 200, "ms": 55},
...     {"endpoint": "/api/users", "method": "POST", "status": 201, "ms": 120},
...     {"endpoint": "/api/orders", "method": "GET", "status": 200, "ms": 30},
...     {"endpoint": "/api/orders", "method": "GET", "status": 200, "ms": 25},
...     {"endpoint": "/api/auth", "method": "POST", "status": 200, "ms": 80},
...     {"endpoint": "/api/auth", "method": "POST", "status": 401, "ms": 15},
...     {"endpoint": "/api/users", "method": "GET", "status": 200, "ms": 40},
...     {"endpoint": "/api/health", "method": "GET", "status": 200, "ms": 5},
... ]
>>> task_d5_endpoint_stats(requests)
[
    {"endpoint": "/api/auth", "count": 2, "avg_ms": 48},
    {"endpoint": "/api/health", "count": 1, "avg_ms": 5},
    {"endpoint": "/api/orders", "count": 2, "avg_ms": 28},
    {"endpoint": "/api/users", "count": 4, "avg_ms": 65},
]
```

<details>
<summary>Эталонное решение</summary>

```python
def task_d5_endpoint_stats(requests):
    stats = {}
    for req in requests:
        ep = req["endpoint"]
        if ep not in stats:
            stats[ep] = {"total_ms": 0, "count": 0}
        stats[ep]["total_ms"] += req["ms"]
        stats[ep]["count"] += 1
    report = []
    for ep, s in sorted(stats.items()):
        report.append({
            "endpoint": ep,
            "count": s["count"],
            "avg_ms": round(s["total_ms"] / s["count"]),
        })
    return report
```

</details>
