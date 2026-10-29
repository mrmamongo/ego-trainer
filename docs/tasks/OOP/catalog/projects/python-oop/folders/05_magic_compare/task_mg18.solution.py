class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __eq__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        return hash((self.rank, self.suit))


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mg18_tally(rows):
    counts = {}
    for rank, suit in rows:
        card = Card(rank, suit)
        counts[card] = counts.get(card, 0) + 1
    return [[card.rank, card.suit, count] for card, count in counts.items()]
