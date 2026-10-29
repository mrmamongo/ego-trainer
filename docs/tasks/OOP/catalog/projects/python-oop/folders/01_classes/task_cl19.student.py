def task_cl19_squad_hp(hps, damage):
    return None  # твой код


# ===== Ниже ничего не меняй: это готовый класс игрока. =====

class GivenPlayer:
    """Готовый игрок: свою версию писать не нужно."""

    def __init__(self, name, hp):
        self.name = name
        self.hp = hp

    def take_damage(self, damage):
        self.hp = self.hp - damage
        if self.hp < 0:
            self.hp = 0
