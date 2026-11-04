class Payment:
    def fee(self, amount):
        return 0


class Card(Payment):
    def fee(self, amount):
        return amount * 2 // 100


class Crypto(Payment):
    def fee(self, amount):
        return 1 + amount // 100


def given_make(kind):
    """Готовый помощник: создаёт способ оплаты по названию."""
    kinds = {"Cash": Payment, "Card": Card, "Crypto": Crypto}
    return kinds[kind]()


def task_in14_fees(kinds, amount):
    result = {}
    for kind in kinds:
        method = given_make(kind)
        result[kind] = method.fee(amount)
    return result
