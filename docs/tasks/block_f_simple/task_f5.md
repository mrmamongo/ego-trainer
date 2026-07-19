# Задача F5: Есть ли VIP-товар в заказе

**Блок:** F — Базовые паттерны
**Сложность:** easy
**Темы:** any, nested structures, early exit

## Условие

Интернет-магазин проверяет заказ на наличие VIP-товара.
Функция возвращает `True`, если хотя бы один товар в заказе имеет категорию `"vip"`.

## Аргументы

- `order` — ОДИН словарь (не список!):
  `{"order_id": "O1", "items": [{"name": "Pen", "category": "stationery"}, {"name": "Watch", "category": "vip"}]}`

## Возвращает

`True` — если хотя бы один item имеет `category == "vip"`.
`False` — если таких нет.
Если `items` пустой — верни `False`.

## Правила

- `True` — если хотя бы один item имеет `category == "vip"`.
- `False` — если нет.
- Если `items` пустой — верни `False`.

## Пример

```python
order = {
    "order_id": "O1",
    "items": [
        {"name": "Bread", "category": "food"},
        {"name": "Gold Watch", "category": "vip"},
        {"name": "Milk", "category": "food"},
    ],
}

task_f5_vip_in_order(order)
# -> True
```

<details>
<summary>Эталонное решение</summary>

```python
def task_f5_vip_in_order(order):
    for item in order.get("items", []):
        if item.get("category") == "vip":
            return True
    return False
```

</details>
