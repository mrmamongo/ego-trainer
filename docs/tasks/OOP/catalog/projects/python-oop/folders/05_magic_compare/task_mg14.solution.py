class Player:
    def __init__(self, name, score):
        self.name = name
        self.score = score

    def __lt__(self, other):
        if self.score != other.score:
            return self.score > other.score
        return self.name < other.name


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mg14_board(rows):
    players = [Player(name, score) for name, score in rows]
    return [player.name for player in sorted(players)]
