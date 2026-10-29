class ProgressBar:
    def __init__(self, percent):
        self.percent = percent

    @property
    def percent(self):
        return self._percent

    @percent.setter
    def percent(self, value):
        if value < 0 or value > 100:
            raise ValueError("процент от 0 до 100")
        self._percent = value

    @property
    def bar(self):
        filled = self._percent // 10
        return "#" * filled + "." * (10 - filled)

    def advance(self, step):
        self.percent = min(100, self.percent + step)


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_pr18_bar(actions):
    return given_same_error(given_play(ProgressBar, actions))


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
