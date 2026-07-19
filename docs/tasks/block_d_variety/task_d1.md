# Задача D1: Выручка по категориям

**Блок:** D — Разные домены
**Сложность:** medium
**Темы:** e-commerce, агрегация, словари-счётчики

## Условие

Функция агрегирует выручку интернет-магазина по категориям товаров. Нужно просуммировать поле `amount` всех заказов в каждой категории и вернуть словарь «категория → суммарная выручка».

## Аргументы

- `orders` — список словарей: `[{"id": "O1", "category": "electronics", "amount": 1200, "status": "paid"}, ...]`

## Возвращает

Словарь: категория -> сумма `amount` ВСЕХ заказов (не только `paid`). Категории без заказов не попадают.

## Правила

- Считаются ВСЕ заказы, независимо от статуса (`status` не учитывается).
- Категории без заказов не попадают в результат.
- Ключ результата — значение поля `category` из заказа.

## Пример

```python
>>> orders = [
...     {"category": "food", "amount": 100},
...     {"category": "food", "amount": 50},
...     {"category": "tech", "amount": 500},
... ]
>>> task_d1_orders_by_category(orders)
{"food": 150, "tech": 500}
```

<details>
<summary>Эталонное решение</summary>

```python
def task_d1_orders_by_category(orders):
    result = {}
    for o in orders:
        cat = o["category"]
        result[cat] = result.get(cat, 0) + o["amount"]
    return result
```

</details>
