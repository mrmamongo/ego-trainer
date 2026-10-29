class Product:
    def __init__(self, name, price, discount=0):
        self.name = name
        self.price = price
        self.discount = discount

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if value <= 0:
            raise ValueError("цена должна быть больше нуля")
        self._price = value

    @property
    def discount(self):
        return self._discount

    @discount.setter
    def discount(self, value):
        if value < 0 or value > 100:
            raise ValueError("скидка от 0 до 100")
        self._discount = value

    @property
    def final_price(self):
        return self._price * (100 - self._discount) // 100


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_pr10_product(actions):
    return given_same_error(given_play(Product, actions))


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
