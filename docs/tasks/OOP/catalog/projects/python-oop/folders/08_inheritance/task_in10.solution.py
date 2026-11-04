class Employee:
    def __init__(self, name, base):
        self.name = name
        self.base = base

    def salary(self):
        return self.base


class Manager(Employee):
    def __init__(self, name, base, bonus):
        super().__init__(name, base)
        self.bonus = bonus

    def salary(self):
        return super().salary() + self.bonus


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_in10_manager(actions):
    return given_play_classes({"Employee": Employee, "Manager": Manager}, actions)


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
