"""XL-M-18 — Исправь loot-table roll (баг: смещение).

MMO loot table: список {"item": ..., "weight": N}.
Функция roll_loot(table, rng_int) выбирает
предмет по весу. Сейчас rng_int сравнивается
с cumulative weight неправильно —
выбор смещён в пользу первого элемента.

Исправь: rng_int из [0, total_weight),
бинарный поиск по кумулятивным весам.
Если table пустой — None.

Пример:
    table = [{"item":"common","weight":90},
             {"item":"rare","weight":10}]
    roll_loot(table, 5)  # "common"
    roll_loot(table, 95) # "rare"
"""


def roll_loot(table, rng_int):
    # Намеренная ошибка: неправильный бинарный поиск
    if not table:
        return None
    cum = 0
    for entry in table:
        cum += entry["weight"]
        if rng_int < cum:
            return entry["item"]
    return table[-1]["item"]


if __name__ == "__main__":
    table = [{"item": "common", "weight": 90}, {"item": "rare", "weight": 10}]
    print(roll_loot(table, 5), roll_loot(table, 95))
