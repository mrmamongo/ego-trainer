class Account:
    """Готовый класс: баланс — свойство, отрицательным он быть не может."""

    def __init__(self, balance):
        self.balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError("баланс не может быть отрицательным")
        self._balance = value


def apply_change(account, delta):
    try:
        account.balance = account.balance + delta
    except ValueError:
        return False
    return True


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_pr12_change(start, deltas):
    account = Account(start)
    results = [apply_change(account, delta) for delta in deltas]
    return {"results": results, "balance": account.balance}
