class Money:
    def __init__(self, kopecks):
        pass  # твой код: запомни kopecks

    def __add__(self, other):
        pass  # твой код: верни новый Money с суммой копеек

    def __sub__(self, other):
        pass  # твой код: верни новый Money с разностью копеек

    def __mul__(self, k):
        pass  # твой код: верни новый Money, копейки умножены на k


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
