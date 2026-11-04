class Payment:
    name = "платёж"

    def fee(self, amount):
        return 0

    def total(self, amount):
        return amount + self.fee(amount)


class Card(Payment):
    name = "карта"

    def fee(self, amount):
        return amount * 2 // 100


class Cash(Payment):
    name = "наличные"


class Crypto(Payment):
    name = "крипта"

    def fee(self, amount):
        return 1 + amount // 100


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_in13_payments(actions):
    return given_play_classes({"Payment": Payment, "Card": Card, "Cash": Cash, "Crypto": Crypto}, actions)


def given_play_classes(classes, actions):
    """Готовый помощник: как given_play, но в "new" первым идёт имя класса, а "is" проверяет isinstance."""
    results = []
    obj = None
    for action in actions:
        name, args = action[0], list(action[1:])
        try:
            if name == "new":
                obj = classes[args[0]](*args[1:])
                result = "ok"
            elif name == "is":
                result = isinstance(obj, classes[args[0]])
            elif name == "get":
                result = getattr(obj, args[0])
            elif name == "set":
                setattr(obj, args[0], args[1])
                result = "ok"
            else:
                result = getattr(obj, name)(*args)
        except Exception as error:
            result = ["error", type(error).__name__, str(error)]
        results.append(given_plain(result))
    return results


def given_plain(value):
    """Числа, строки, True/False, None, списки и словари из них — как есть; объект — имя его класса."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (list, tuple)):
        return [given_plain(item) for item in value]
    if isinstance(value, dict):
        return {key: given_plain(item) for key, item in value.items()}
    return type(value).__name__
