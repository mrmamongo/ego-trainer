class Discount:
    def apply(self, price):
        return price


class Percent(Discount):
    def __init__(self, percent):
        self.percent = percent

    def aply(self, price):
        return price - price * self.percent // 100


class Fixed(Discount):
    def __init__(self, amount):
        self.amount = amount

    def apply(self, price):
        return max(0, price - self.amount)


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_in16_discount(actions):
    return given_play_classes({"Discount": Discount, "Percent": Percent, "Fixed": Fixed}, actions)


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
