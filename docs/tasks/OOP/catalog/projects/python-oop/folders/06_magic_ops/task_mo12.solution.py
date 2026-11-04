class Money:
    def __init__(self, kopecks):
        self.kopecks = kopecks

    def __add__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return Money(self.kopecks + other.kopecks)


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mo12_add(rows):
    results = []
    for left, kind, value, reverse in rows:
        first = Money(left)
        other = Money(value) if kind == "money" else value
        try:
            direct = first.__add__(other) is NotImplemented
        except Exception:
            direct = False
        try:
            total = other + first if reverse else first + other
            answer = total.kopecks
        except TypeError:
            answer = "TypeError"
        results.append([answer, direct])
    return results
