class BudgetError(Exception):
    pass


def spend(balance, amount):
    if amount <= 0:
        raise ValueError("сумма должна быть больше нуля")
    if amount > balance:
        raise BudgetError("не хватает денег")
    return balance - amount


def task_er10_pay(balance, amount):
    try:
        new_balance = spend(balance, amount)
    except BudgetError:
        return {"status": "rejected", "reason": "budget"}
    except ValueError:
        return {"status": "rejected", "reason": "bad_amount"}
    return {"status": "done", "balance": new_balance}
