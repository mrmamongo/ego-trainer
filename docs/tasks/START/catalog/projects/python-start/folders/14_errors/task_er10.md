---
id: ER10
title: "Своя ошибка BudgetError"
version: "1.0.0"
level: medium
tags: [errors, write, custom-exception]
breaking: false
theory: [er-custom, er-raise]
---

# Задача ER10: Своя ошибка BudgetError

## Условие

### Как это работает

Своё исключение объявляют одной формулой (устройство `class` мы разберём позже):

```python
class BudgetError(Exception):
    pass
```

После этого `BudgetError` можно бросать и ловить так же, как `ValueError`. Низкоуровневая функция бросает, а та, что отвечает за ответ пользователю, ловит и превращает ошибку в словарь:

```python
def withdraw(balance, amount):
    if amount > balance:
        raise BudgetError("не хватает денег")
    return balance - amount

def cash_out(balance, amount):
    try:
        new_balance = withdraw(balance, amount)
    except BudgetError:
        return {"status": "rejected", "reason": "budget"}
    return {"status": "done", "balance": new_balance}
```

Несколько `except` подряд позволяют по-разному ответить на разные ошибки: Python берёт первый подходящий сверху вниз. Ловить нужно **конкретный** тип: `except BudgetError`, а не общий `except Exception`.

### Задание

В файле задачи три шага:

1. Объяви класс `BudgetError(Exception)` с `pass` внутри.
2. Напиши `spend(balance, amount)`: если `amount` не больше нуля, брось `ValueError("сумма должна быть больше нуля")`; если `amount` больше `balance`, брось `BudgetError("не хватает денег")`; иначе верни `balance - amount`. Проверки идут именно в таком порядке.
3. Напиши `task_er10_pay(balance, amount)`: вызови `spend` и верни

   - `{"status": "done", "balance": <новый баланс>}`, если всё получилось;
   - `{"status": "rejected", "reason": "budget"}`, если поймана `BudgetError`;
   - `{"status": "rejected", "reason": "bad_amount"}`, если поймана `ValueError`.

## Аргументы

- `balance` — целое число, баланс (не меньше нуля).
- `amount` — целое число, сумма платежа (может быть нулём или отрицательной).

## Возвращает

Словарь из пункта 3.

## Правила

- `BudgetError` объяви сам, а исключения бросай командой `raise`.
- В `pay` ловить нужно только `BudgetError` и `ValueError`, а не `Exception` и не голый `except:`.
- Функция должна **вернуть** значение через `return`, а не печатать его.

## Пример

```python
task_er10_pay(100, 30)    # -> {"status": "done", "balance": 70}
task_er10_pay(100, 130)   # -> {"status": "rejected", "reason": "budget"}
task_er10_pay(100, 0)     # -> {"status": "rejected", "reason": "bad_amount"}
```

## Учебные цели

- Объявить своё исключение и бросить его.
- Поймать разные ошибки разными `except` и превратить их в код отказа.

## Проверка понимания

Почему при `amount = 0` получается `bad_amount`, а не `done` с прежним балансом? Что бы изменилось, если бы `spend` бросала `ValueError` и в случае нехватки денег?
