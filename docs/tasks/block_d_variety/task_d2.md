# Задача D2: Алёрты по сенсорам

**Блок:** D — Разные домены
**Сложность:** medium
**Темы:** IoT, сенсоры, фильтрация, множества

## Условие

Функция анализирует показания IoT-сенсоров и возвращает список идентификаторов сенсоров, у которых зафиксировано превышение пороговых значений. Алёрт срабатывает, если температура выше 80 или влажность выше 70.

## Аргументы

- `readings` — список словарей: `[{"sensor_id": "S1", "temperature": 85, "humidity": 40}, ...]`

## Возвращает

Список `sensor_id`, где `temperature > 80` ИЛИ `humidity > 70`. Без дубликатов. Порядок не важен.

## Правила

- Условие алёрта: `temperature > 80` ИЛИ `humidity > 70`.
- Дубликаты `sensor_id` исключаются (один сенсор — одна запись в результате).
- Порядок элементов в списке не важен.

## Пример

```python
>>> readings = [
...     {"sensor_id": "S1", "temperature": 72, "humidity": 35},
...     {"sensor_id": "S2", "temperature": 92, "humidity": 40},
...     {"sensor_id": "S3", "temperature": 68, "humidity": 75},
...     {"sensor_id": "S4", "temperature": 85, "humidity": 80},
...     {"sensor_id": "S2", "temperature": 88, "humidity": 45},
...     {"sensor_id": "S5", "temperature": 55, "humidity": 30},
... ]
>>> task_d2_sensor_alerts(readings)
["S2", "S3", "S4"]
```

<details>
<summary>Эталонное решение</summary>

```python
def task_d2_sensor_alerts(readings):
    alerts = set()
    for r in readings:
        if r["temperature"] > 80 or r["humidity"] > 70:
            alerts.add(r["sensor_id"])
    return list(alerts)
```

</details>
