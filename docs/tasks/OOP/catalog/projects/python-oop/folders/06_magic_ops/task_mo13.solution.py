class Score:
    def __init__(self, points):
        self.points = points

    def __add__(self, other):
        if not isinstance(other, Score):
            return NotImplemented
        return Score(self.points + other.points)

    def __radd__(self, other):
        if other == 0:
            return self
        return NotImplemented


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mo13_total(points, start):
    try:
        total = sum([Score(p) for p in points], start)
    except TypeError:
        return "TypeError"
    return total.points if isinstance(total, Score) else total
