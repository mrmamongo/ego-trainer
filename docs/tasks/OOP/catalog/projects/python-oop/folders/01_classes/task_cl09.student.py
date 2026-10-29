class Timer:
    def __init__(self, seconds):
        # твой код: запомни оставшееся время в атрибуте seconds_left
        pass

    def tick(self):
        # твой код: уменьши seconds_left на 1, но не ниже нуля
        pass

    def is_over(self):
        # твой код: верни True, если время вышло
        return None


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_cl09_timer(actions):
    return given_play(Timer, actions)


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
