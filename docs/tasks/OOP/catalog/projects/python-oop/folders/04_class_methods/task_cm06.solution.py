def add_bonus(func):
    def wrapper(*args):
        result = func(*args)
        result = result + 5
        return result
    return wrapper


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def given_hit(power, level):
    return power * level


def task_cm06_bonus(power, level):
    hit = add_bonus(given_hit)
    return hit(power, level)
