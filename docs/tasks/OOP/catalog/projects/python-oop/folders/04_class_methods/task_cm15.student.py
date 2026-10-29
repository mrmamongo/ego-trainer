class Player:
    def __init__(self, name, hp, level=1):
        pass  # твой код

    @classmethod
    def from_dict(cls, data):
        return None  # твой код


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_cm15_load(save):
    player = Player.from_dict(save)
    return [player.name, player.hp, player.level]
