class MessageCounter:
    def __init__(self):
        # твой код: заведи атрибуты count (сколько сообщений) и last_author (кто писал последним)
        pass

    def post(self, author):
        # твой код: учти новое сообщение
        pass

    def is_quiet(self):
        # твой код: верни True, если сообщений ещё не было
        return None


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_cl06_chat(actions):
    return given_play(MessageCounter, actions)


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
