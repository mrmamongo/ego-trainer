class Money:
    def __init__(self, kopecks):
        self.kopecks = kopecks

    def __add__(self, other):
        if not isinstance(other, Money):
            return None
        return Money(self.kopecks + other.kopecks)


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mo06_add(rows):
    results = []
    for left, kind, value in rows:
        other = Money(value) if kind == "money" else value
        try:
            total = Money(left) + other
        except TypeError:
            results.append("TypeError")
            continue
        if isinstance(total, Money):
            results.append(total.kopecks)
        else:
            results.append("без ошибки: " + type(total).__name__)
    return results
