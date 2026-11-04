class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __mul__(self, k):
        if not isinstance(k, (int, float)):
            return NotImplemented
        return Vector2(self.x * k, self.y * k)

    def __rmul__(self, k):
        return self.__mul__(k)


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mo18_scale(x, y, k):
    v = Vector2(x, y)
    return [given_try(lambda: v * k), given_try(lambda: k * v)]


def given_try(func):
    """Готовый помощник: вызывает func и возвращает [x, y] вектора или слово «TypeError»."""
    try:
        result = func()
    except TypeError:
        return "TypeError"
    return [result.x, result.y]
