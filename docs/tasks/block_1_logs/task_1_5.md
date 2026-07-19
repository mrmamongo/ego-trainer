# Задача 1.5: SLA-отчёт

**Блок:** 1 — Логи (агрегация)
**Сложность:** medium
**Темы:** логи, агрегация, SLA, группировка, округление, сортировка

## Условие

Функция строит SLA-отчёт по каждому сервису: считает общее число запросов, число успешных (статусы 200–299) и процент успешности. Это сводный отчёт, по которому видно, какие сервисы не дотягивают до целевого SLA.

## Аргументы

- `logs` — список словарей. У каждого есть ключи `"service"` и `"status"`.

## Возвращает

Список словарей (по одному на каждый сервис):

```python
[
    {"service": "api",   "total": 100, "success": 95, "sla_percent": 95},
    {"service": "auth",  "total": 80,  "success": 72, "sla_percent": 90},
    ...
]
```

## Правила

- `total` = сколько всего запросов к сервису.
- `success` = сколько из них со статусом 200..299.
- `sla_percent` = округлить до целого: `(success / total) * 100`.
- Порядок сервисов: по алфавиту (`sorted`).

## Пример

```python
>>> task_1_5_sla_report(logs)
[
    {"service": "api",   "total": 100, "success": 95, "sla_percent": 95},
    {"service": "auth",  "total": 80,  "success": 72, "sla_percent": 90},
]
```

<details>
<summary>Эталонное решение</summary>

```python
def task_1_5_sla_report(logs):
    stats = {}
    for e in logs:
        svc = e["service"]
        if svc not in stats:
            stats[svc] = {"total": 0, "success": 0}
        stats[svc]["total"] += 1
        if 200 <= e["status"] <= 299:
            stats[svc]["success"] += 1
    report = []
    for svc, s in sorted(stats.items()):
        sla = round((s["success"] / s["total"]) * 100)
        report.append({
            "service": svc, "total": s["total"],
            "success": s["success"], "sla_percent": sla,
        })
    return report
```

</details>
