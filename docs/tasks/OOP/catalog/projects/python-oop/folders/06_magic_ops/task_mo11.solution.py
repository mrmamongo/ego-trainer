class Money:
    def __init__(self, kopecks):
        self.kopecks = kopecks

    def __add__(self, other):
        return Money(self.kopecks + other.kopecks)

    def __sub__(self, other):
        return Money(self.kopecks - other.kopecks)

    def __mul__(self, k):
        return Money(self.kopecks * k)


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mo11_calc(a, b, k):
    left = Money(a)
    right = Money(b)
    total = left + right
    return {
        "sum": total.kopecks,
        "diff": (left - right).kopecks,
        "times": (left * k).kopecks,
        "a": left.kopecks,
        "b": right.kopecks,
        "new_objects": total is not left and total is not right,
    }
