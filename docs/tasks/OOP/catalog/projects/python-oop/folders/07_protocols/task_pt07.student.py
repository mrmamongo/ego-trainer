class Transaction:
    def __init__(self, wallet):
        self.wallet = wallet

    def __enter__(self):
        self.saved = self.wallet.balance
        return self.wallet

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:
            self.wallet.balance = self.saved
        return True


# ===== Ниже ничего не меняй: это рамка для проверки. =====

class GivenWallet:
    """Готовый кошелёк: у него только баланс."""

    def __init__(self, balance):
        self.balance = balance


def task_pt07_run(balance, spends):
    wallet = GivenWallet(balance)
    raised = False
    try:
        with Transaction(wallet) as w:
            for amount in spends:
                if amount > w.balance:
                    raise ValueError("недостаточно денег")
                w.balance -= amount
    except ValueError:
        raised = True
    return [wallet.balance, raised]
