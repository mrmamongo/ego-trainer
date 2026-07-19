# Задача H2: Таблица дропа с шансами

**Блок:** H — Игры
**Сложность:** medium
**Темы:** лут, random, вероятность, сид

## Условие

Дана таблица дропа: для каждого предмета указан шанс выпадения (в процентах) и диапазон количества. Функция должна с фиксированным сидом определить, выпал ли каждый предмет, и сколько именно единиц выпало.

## Аргументы

- `drops` — список словарей вида `[{"item": "Gold", "chance": 100, "min": 5, "max": 15}, {"item": "Iron Dagger", "chance": 30, "min": 1, "max": 1}]`
- `seed` — seed для `random` (фиксированный для проверки), по умолчанию `42`

## Возвращает

Словарь: `item` -> сколько выпало (`0`, если не выпало). Например: `{"Gold": 12, "Iron Dagger": 0}`

## Правила

- Зафиксировать `random.seed(seed)` (или создать `random.Random(seed)`).
- Для каждого дропа: `random.randint(1, 100) <= chance` → выпало.
- Если выпало → количество = `random.randint(min, max)`.
- Если не выпало → `0`.

## Пример

```python
drops = [
    {"item": "Gold", "chance": 100, "min": 5, "max": 15},
    {"item": "Iron Dagger", "chance": 30, "min": 1, "max": 1},
]
# → {"Gold": 12, "Iron Dagger": 0}
```

<details>
<summary>Эталонное решение</summary>

```python
import random

def task_h2_loot_drop(drops, seed=42):
    rng = random.Random(seed)
    result = {}
    for d in drops:
        roll = rng.randint(1, 100)
        if roll <= d["chance"]:
            result[d["item"]] = rng.randint(d["min"], d["max"])
        else:
            result[d["item"]] = 0
    return result
```

</details>
