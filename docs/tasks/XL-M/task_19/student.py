"""XL-M-19 — Исправь cooldown ability (баг: повторный cast).

У ability есть cooldown в секундах.
Функция try_cast(ability, now_sec) возвращает
True и обновляет ability["last_cast"] если cooldown
прошёл, иначе False. Сейчас last_cast не
обновляется при успешном касте — ability
можно кастить бесконечно.

Исправь: при успехе запиши now_sec
в ability["last_cast"]. last_cast может
отсутствовать (тогда каст всегда разрешён).

Пример:
    ab = {"name": "fireball", "cooldown": 5, "last_cast": 0}
    try_cast(ab, 3)  # False (3 < 0+5)
    try_cast(ab, 6)  # True, last_cast → 6
    try_cast(ab, 7)  # False
"""


def try_cast(ability, now_sec):
    cd = ability["cooldown"]
    last = ability.get("last_cast", 0)
    if now_sec - last >= cd:
        return True
    return False


if __name__ == "__main__":
    ab = {"name": "fireball", "cooldown": 5, "last_cast": 0}
    print(try_cast(ab, 6))
