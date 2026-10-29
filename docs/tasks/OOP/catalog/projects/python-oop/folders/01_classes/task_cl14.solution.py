class Inventory:
    def __init__(self):
        self.items = {}

    def add(self, name, qty):
        self.items[name] = self.items.get(name, 0) + qty

    def count(self, name):
        return self.items.get(name, 0)

    def total(self):
        total = 0
        for qty in self.items.values():
            total = total + qty
        return total


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_cl14_inventory(actions):
    return given_play(Inventory, actions)


def given_play(cls, actions):
    """Готовый помощник: создаёт объект и по очереди выполняет действия сценария."""
    results = []
    obj = None
    for action in actions:
        name, args = action[0], list(action[1:])
        try:
            if name == "new":
                obj = cls(*args)
                result = "ok"
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
