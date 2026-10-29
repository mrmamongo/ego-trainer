class Player:
    def __init__(self, name, score):
        self.name = name
        self.score = score

    def __repr__(self):
        return f"Player('{self.name}', {self.score})"

    def __str__(self):
        return f"{self.name}: {self.score}"


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mg08_lines(rows):
    players = [Player(name, score) for name, score in rows]
    return [[str(player), repr(player), f"{player}"] for player in players]
