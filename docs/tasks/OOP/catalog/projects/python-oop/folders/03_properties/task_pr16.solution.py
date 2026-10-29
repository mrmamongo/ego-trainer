class Quest:
    def __init__(self, title, base_reward, level=1):
        self._title = title
        self.base_reward = base_reward
        self._done = False
        self.level = level

    @property
    def title(self):
        return self._title

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        if value < 1 or value > 5:
            raise ValueError("уровень от 1 до 5")
        self._level = value

    @property
    def reward(self):
        return self.base_reward * self._level

    @property
    def done(self):
        return self._done

    def complete(self):
        if self._done:
            raise ValueError("квест уже выполнен")
        self._done = True
        return self.reward


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_pr16_quest(actions):
    return given_same_error(given_play(Quest, actions))


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
