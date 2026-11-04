class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mo05_move(start, step):
    p = Vector2(start[0], start[1])
    q = Vector2(step[0], step[1])
    r = p + q
    return {"result": [r.x, r.y], "start": [p.x, p.y], "step": [q.x, q.y], "same_object": r is p}
