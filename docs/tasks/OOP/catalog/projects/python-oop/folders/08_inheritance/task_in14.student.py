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
    # Собери тело функции из строк ниже. Они перемешаны и записаны без отступов:
    # порядок и отступы придётся расставить самому. Лишних строк нет.
    #
    #   return result
    #   result[kind] = method.fee(amount)
    #   result = {}
    #   method = given_make(kind)
    #   for kind in kinds:
    #
    return None  # собери тело функции из строк выше
