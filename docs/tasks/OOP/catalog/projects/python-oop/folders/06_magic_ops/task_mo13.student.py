class Score:
    def __init__(self, points):
        pass  # твой код: запомни points

    def __add__(self, other):
        pass  # твой код: сумма двух Score, для чужого типа верни NotImplemented

    def __radd__(self, other):
        pass  # твой код: для 0 верни self, иначе NotImplemented


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mo13_total(points, start):
    try:
        total = sum([Score(p) for p in points], start)
    except TypeError:
        return "TypeError"
    return total.points if isinstance(total, Score) else total
