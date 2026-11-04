from contextlib import contextmanager


@contextmanager
def transaction(wallet):
    saved = wallet.balance
    try:
        yield wallet
    except Exception:
        wallet.balance = saved
        raise


# ===== Ниже ничего не меняй: это рамка для проверки. =====

class GivenWallet:
    """Готовый кошелёк: у него только баланс."""

    def __init__(self, balance):
        self.balance = balance


def task_pt15_run(balance, spends):
    wallet = GivenWallet(balance)
    raised = False
    try:
        with transaction(wallet) as w:
            for amount in spends:
                if amount > w.balance:
                    raise ValueError("недостаточно денег")
                w.balance -= amount
    except ValueError:
        raised = True
    return [wallet.balance, raised]
