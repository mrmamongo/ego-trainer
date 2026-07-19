# Задача H4: Рюкзак: взять максимум ценного

**Блок:** H — Игры
**Сложность:** medium
**Темы:** рюкзак, жадный алгоритм, оптимизация

## Условие

Игрок собирает добычу в рюкзак ограниченной вместимости. Предметы уже отсортированы по убыванию ценности на единицу веса. Нужно жадно набрать предметы, беря их по порядку, пока они влезают по весу, и вернуть итоговый набор с подсчётом веса и ценности.

## Аргументы

- `items` — список словарей, отсортированных по убыванию ценность/вес: `[{"name": "Sword", "weight": 3, "value": 150}, {"name": "Shield", "weight": 5, "value": 120}, {"name": "Potion", "weight": 1, "value": 40}]`
- `capacity` — максимальный вес рюкзака (целое число)

## Возвращает

Словарь:
```python
{
    "taken": [{"name": "Sword", "weight": 3, "value": 150}, ...],
    "total_weight": N,
    "total_value": N,
    "remaining_capacity": N
}
```

## Правила

- Алгоритм жадный: берём предметы по порядку, пока влезает по весу.
- Если предмет не влезает — пропускаем, идём к следующему.
- `total_weight` — суммарный вес взятых предметов.
- `total_value` — суммарная ценность взятых предметов.
- `remaining_capacity` — остаток вместимости (`capacity - total_weight`).

## Пример

```python
items = [
    {"name": "Sword", "weight": 3, "value": 150},
    {"name": "Shield", "weight": 5, "value": 120},
    {"name": "Potion", "weight": 1, "value": 40},
]
capacity = 8
# → {"taken": [{"name": "Sword", ...}, {"name": "Potion", ...}],
#    "total_weight": 4, "total_value": 190, "remaining_capacity": 4}
```

<details>
<summary>Эталонное решение</summary>

```python
def task_h4_backpack(items, capacity):
    taken = []
    total_w = 0
    total_v = 0
    for item in items:
        if total_w + item["weight"] <= capacity:
            taken.append(item)
            total_w += item["weight"]
            total_v += item["value"]
    return {
        "taken": taken,
        "total_weight": total_w,
        "total_value": total_v,
        "remaining_capacity": capacity - total_w,
    }
```

</details>
