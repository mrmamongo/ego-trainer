# Задача D4: Стоимость инвентаря по редкости

**Блок:** D — Разные домены
**Сложность:** medium
**Темы:** game, инвентарь, агрегация, словари-счётчики

## Условие

Функция подсчитывает общую стоимость игрового инвентаря, сгруппированного по редкости предметов. Стоимость каждой позиции равна `qty * unit_price`; суммы накапливаются по каждой категории редкости.

## Аргументы

- `inventory` — список словарей: `[{"item": "Sword", "rarity": "rare", "qty": 2, "unit_price": 150}, ...]`

## Возвращает

Словарь: `rarity` -> общая стоимость (`qty * unit_price`). `rarity` с маленькой буквы, как в данных.

## Правила

- Стоимость позиции = `qty * unit_price`.
- Результат группируется по полю `rarity`.
- Ключ берётся как есть из данных (с маленькой буквы, без преобразования регистра).
- Редкости без предметов не попадают в результат.

## Пример

```python
>>> inventory = [
...     {"item": "Iron Sword", "rarity": "common", "qty": 3, "unit_price": 50},
...     {"item": "Dragon Scale", "rarity": "legendary", "qty": 1, "unit_price": 5000},
...     {"item": "Health Potion", "rarity": "common", "qty": 10, "unit_price": 15},
...     {"item": "Enchanted Bow", "rarity": "rare", "qty": 1, "unit_price": 300},
...     {"item": "Gold Ring", "rarity": "rare", "qty": 2, "unit_price": 250},
...     {"item": "Phoenix Feather", "rarity": "legendary", "qty": 1, "unit_price": 8000},
... ]
>>> task_d4_inventory_value(inventory)
{"common": 300, "legendary": 13000, "rare": 800}
```

<details>
<summary>Эталонное решение</summary>

```python
def task_d4_inventory_value(inventory):
    result = {}
    for item in inventory:
        rar = item["rarity"]
        value = item["qty"] * item["unit_price"]
        result[rar] = result.get(rar, 0) + value
    return result
```

</details>
