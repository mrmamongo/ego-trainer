class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __mul__(self, k):
        return None  # вместо None впиши новый Vector2 с координатами self.x * k и self.y * k


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mo08_scale(x, y, k):
    v = Vector2(x, y)
    w = v * k
    return {"scaled": [w.x, w.y], "original": [v.x, v.y]}
