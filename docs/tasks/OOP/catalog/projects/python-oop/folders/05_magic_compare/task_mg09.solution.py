class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __eq__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.rank == other.rank and self.suit == other.suit


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mg09_compare(pairs):
    results = []
    for first, second in pairs:
        a = Card(first[0], first[1])
        b = Card(second[0], second[1])
        results.append([a == b, a != b, a == first[0]])
    return results
