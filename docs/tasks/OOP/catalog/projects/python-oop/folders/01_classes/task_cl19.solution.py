def task_cl19_squad_hp(hps, damage):
    squad = []
    for hp in hps:
        squad.append(GivenPlayer("бот", hp))
    for player in squad:
        player.take_damage(damage)
    result = []
    for player in squad:
        result.append(player.hp)
    return result


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
