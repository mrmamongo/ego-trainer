class BankAccount:
    def __init__(self, owner, balance):
        pass  # твой код: owner запомни в _owner, balance запиши через свойство

    @property
    def owner(self):
        pass  # твой код

    @property
    def balance(self):
        pass  # твой код

    @balance.setter
    def balance(self, value):
        pass  # твой код

    def deposit(self, amount):
        pass  # твой код

    def withdraw(self, amount):
        pass  # твой код


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_pr14_account(actions):
    return given_same_error(given_play(BankAccount, actions))


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


def given_same_error(results):
    """Текст ошибки AttributeError зависит от версии Python, поэтому рамка оставляет только её тип."""
    fixed = []
    for result in results:
        if isinstance(result, list) and result[:2] == ["error", "AttributeError"]:
            result = ["error", "AttributeError", ""]
        fixed.append(result)
    return fixed
