class Quest:
    def __init__(self, title):
        self.title = title
        self.status = "new"

    def start(self):
        if self.status != "new":
            raise ValueError(f"нельзя начать квест из статуса {self.status}")
        self.status = "active"

    def finish(self):
        if self.status != "active":
            raise ValueError(f"нельзя завершить квест из статуса {self.status}")
        self.status = "done"

    def is_done(self):
        return self.status == "done"


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_cl17_quest(actions):
    return given_play(Quest, actions)


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
