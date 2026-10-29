class BankAccount:
    def __init__(self, owner, balance):
        self._owner = owner
        self.balance = balance

    @property
    def owner(self):
        return self._owner

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError("баланс не может быть отрицательным")
        self._balance = value

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("сумма должна быть больше нуля")
        self.balance = self.balance + amount

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("сумма должна быть больше нуля")
        self.balance = self.balance - amount


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
