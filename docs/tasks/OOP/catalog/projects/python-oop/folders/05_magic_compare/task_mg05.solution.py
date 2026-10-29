class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f"Card('{self.rank}', '{self.suit}')"


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mg05_show(rows):
    cards = [Card(rank, suit) for rank, suit in rows]
    return {
        "one": [given_text(repr, card) for card in cards],
        "in_list": given_text(str, cards),
    }


def given_text(func, value):
    """Готовый помощник: вызывает repr или str; если __repr__ сломан, вернёт слово «TypeError»."""
    try:
        return func(value)
    except TypeError:
        return "TypeError"
