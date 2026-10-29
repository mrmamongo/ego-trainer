class Player:
    def __init__(self, name, hp, level=1):
        self.name = name
        self.hp = hp
        self.level = level

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data.get("hp", 100), data.get("level", 1))


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_cm15_load(save):
    player = Player.from_dict(save)
    return [player.name, player.hp, player.level]
