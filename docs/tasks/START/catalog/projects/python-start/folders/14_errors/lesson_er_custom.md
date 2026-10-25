---
id: er-custom
title: "Своё исключение: class BudgetError(Exception)"
order: 4
version: "1.0.0"
---

# Своё исключение: class BudgetError(Exception)

Готовых типов ошибок хватает не всегда. Если «не хватает денег» — особый случай продукта, ему можно дать **собственное имя**:

```python
class BudgetError(Exception):
    pass
```

Пока считай эту запись **готовой формулой**: «так объявляют новый тип ошибки». Слово `class` и устройство классов мы разберём позже; сейчас важно только, что после этого объявления `BudgetError` можно бросать и ловить, как `ValueError`.

```python
def spend(balance, amount):
    if amount > balance:
        raise BudgetError("не хватает денег")
    return balance - amount

def pay(balance, amount):
    try:
        new_balance = spend(balance, amount)
    except BudgetError:
        return {"status": "rejected", "reason": "budget"}
    return {"status": "done", "balance": new_balance}
```

| Вызов | Что произойдёт |
|---|---|
| `pay(100, 30)` | `spend` вернёт `70`, получится `{"status": "done", "balance": 70}` |
| `pay(100, 130)` | `spend` бросит `BudgetError`, `pay` поймает её: `{"status": "rejected", "reason": "budget"}` |

## Зачем своё имя

1. **Точный перехват.** `except BudgetError` не заденет `ValueError` из-за опечатки или плохого ввода. Баги не прячутся.
2. **Читаемость.** По имени понятно, что случилось.
3. **Разные ответы на разные ошибки.** Можно поставить несколько `except` подряд:

```python
try:
    new_balance = spend(balance, amount)
except BudgetError:
    return {"status": "rejected", "reason": "budget"}
except ValueError:
    return {"status": "rejected", "reason": "bad_amount"}
```

Python проверяет `except` сверху вниз и выбирает первый подходящий.

## Частые ошибки

Забыть `(Exception)` в скобках: `class BudgetError:` — это уже не исключение, `raise` такой класс не примет.

Поймать слишком широко: `except Exception:` поймает и `BudgetError`, и опечатки, и всё остальное. Ловить надо именно свой тип.

## Проверь себя

```python
class LimitError(Exception):
    pass

def add(count, limit):
    if count >= limit:
        raise LimitError("лимит")
    return count + 1
```

1. Что вернёт `add(1, 5)`?
2. Что случится при `add(5, 5)`, если вызов стоит в `try: … except ValueError:`?

<details><summary>Ответ</summary>

1. `2`.
2. `LimitError` не является `ValueError`, поэтому `except ValueError` её не поймает, и ошибка всплывёт наружу.

</details>
