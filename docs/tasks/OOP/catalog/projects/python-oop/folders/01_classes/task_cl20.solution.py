class Player:
    def __init__(self, name, hp, armor=0):
        self.name = name
        self.hp = hp
        self.armor = armor

    def take_damage(self, damage):
        real = damage - self.armor
        if real < 0:
            real = 0
        self.hp = self.hp - real
        if self.hp < 0:
            self.hp = 0
        return self.hp


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_cl20_armor(actions):
    return given_play(Player, actions)


def given_play(cls, actions):
    """Готовый помощник: создаёт объект и по очереди выполняет действия сценария."""
    results = []
    obj = None
    for action in actions:
        name, args = action[0], list(action[1:])
        try:
            if name == "new":
                obj = cls(*args)
                result = "ok"
            elif name == "get":
                result = getattr(obj, args[0])
            elif name == "set":
                setattr(obj, args[0], args[1])
                result = "ok"
            else:
                result = getattr(obj, name)(*args)
        except Exception as error:
            result = ["error", type(error).__name__, str(error)]
        results.append(given_plain(result))
    return results


def given_plain(value):
    """Числа, строки, True/False, None, списки и словари из них — как есть; объект — имя его класса."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (list, tuple)):
        return [given_plain(item) for item in value]
    if isinstance(value, dict):
        return {key: given_plain(item) for key, item in value.items()}
    return type(value).__name__
