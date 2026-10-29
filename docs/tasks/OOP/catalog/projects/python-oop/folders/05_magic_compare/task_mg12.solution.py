class Money:
    def __init__(self, kopecks):
        self.kopecks = kopecks

    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return self.kopecks == other.kopecks


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mg12_compare(pairs):
    results = []
    for left, right in pairs:
        a = Money(left)
        b = Money(right)
        results.append([a == b, a != b, a == left, a == GivenAnything()])
    return results


class GivenAnything:
    """Готовый помощник: считает себя равным чему угодно, если его спросят."""

    def __eq__(self, other):
        return True
