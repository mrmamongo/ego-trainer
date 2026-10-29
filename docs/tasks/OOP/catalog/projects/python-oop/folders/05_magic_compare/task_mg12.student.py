class Money:
    def __init__(self, kopecks):
        pass  # твой код: запомни kopecks

    def __eq__(self, other):
        pass  # твой код: сравни суммы, а для других типов верни NotImplemented


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
