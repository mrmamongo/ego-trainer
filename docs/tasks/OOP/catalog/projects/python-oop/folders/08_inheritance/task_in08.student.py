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
    # Собери тело функции из строк ниже. Они перемешаны и записаны без отступов:
    # порядок и отступы придётся расставить самому. Лишних строк нет.
    #
    #   return total
    #   unit = given_make(kind)
    #   for kind in kinds:
    #   total = total + unit.attack()
    #   total = 0
    #
    return None  # собери тело функции из строк выше
