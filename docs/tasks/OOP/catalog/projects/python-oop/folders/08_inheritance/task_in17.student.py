from abc import ABC, abstractmethod


class Status:  # твой код: сделай класс абстрактным
    def label(self):
        return None  # твой код: этот метод должен быть абстрактным

    def can_cancel(self):
        return None  # твой код: этот метод тоже должен быть абстрактным

    def describe(self):
        return None  # твой код


class Created(Status):
    def label(self):
        return None  # твой код

    def can_cancel(self):
        return None  # твой код


class Paid(Status):
    def label(self):
        return None  # твой код

    def can_cancel(self):
        return None  # твой код


class Shipped(Status):
    def label(self):
        return None  # твой код

    def can_cancel(self):
        return None  # твой код


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_in17_status(actions):
    classes = {"Status": Status, "Created": Created, "Paid": Paid, "Shipped": Shipped, "Half": GivenHalf}
    return given_short_errors(given_play_classes(classes, actions))


class GivenHalf(Status):
    """Готовый класс для проверки: умеет только label, поэтому создать его нельзя."""

    def label(self):
        return "половина"


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


def given_short_errors(results):
    """Готовый помощник: у ошибки TypeError оставляет только тип, без текста (текст зависит от версии Python)."""
    short = []
    for result in results:
        if isinstance(result, list) and len(result) == 3 and result[0] == "error" and result[1] == "TypeError":
            result = ["error", "TypeError"]
        short.append(result)
    return short
