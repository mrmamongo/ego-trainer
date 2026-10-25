# Шаг 1: объяви здесь свой тип ошибки BudgetError (формула: class Имя(Exception) и pass).


def spend(balance, amount):
    # Шаг 2: amount <= 0 -> ValueError("сумма должна быть больше нуля");
    # amount > balance -> BudgetError("не хватает денег"); иначе верни balance - amount.
    return None


def task_er10_pay(balance, amount):
    # Шаг 3: вызови spend и верни словарь:
    # {"status": "done", "balance": ...}, или {"status": "rejected", "reason": "budget"},
    # или {"status": "rejected", "reason": "bad_amount"}.
    return None
