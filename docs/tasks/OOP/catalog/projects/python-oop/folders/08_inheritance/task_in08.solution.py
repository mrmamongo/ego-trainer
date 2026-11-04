class Unit:
    def __init__(self, name):
        self.name = name

    def attack(self):
        return 5


class Warrior(Unit):
    def attack(self):
        return 12


class Mage(Unit):
    def attack(self):
        return 9


def given_make(kind):
    """Готовый помощник: создаёт юнита по названию вида."""
    kinds = {"Unit": Unit, "Warrior": Warrior, "Mage": Mage}
    return kinds[kind]("Имя")


def task_in08_total_damage(kinds):
    total = 0
    for kind in kinds:
        unit = given_make(kind)
        total = total + unit.attack()
    return total
