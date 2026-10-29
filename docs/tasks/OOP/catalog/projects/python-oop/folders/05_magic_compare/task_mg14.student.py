class Player:
    def __init__(self, name, score):
        pass  # твой код: запомни name и score

    def __lt__(self, other):
        pass  # твой код: больше очков значит «раньше»; при равенстве по имени


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mg14_board(rows):
    players = [Player(name, score) for name, score in rows]
    return [player.name for player in sorted(players)]
