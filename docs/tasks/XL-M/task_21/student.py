"""XL-M-21 — Исправь экономику MMO (баг: двойной расход).

Функция buy_item(player, item_cost) тратит
item_cost золота. Сейчас стоимость
вычитается ДВАЖЫ — сначала в check,
потом в commit. В результате игрок
платит double.

Исправь: вычти стоимость ОДИН раз,
проверь достаточность ДО вычета.
Если не хватает — верни {"ok": False,
"gold": unchanged}. Успех — {"ok": True,
"gold": new_balance}. Не мутируй player
напрямую — верни новый dict.

Пример:
    buy_item({"gold": 100}, 30)
    == {"ok": True, "gold": 70}
    buy_item({"gold": 10}, 30)
    == {"ok": False, "gold": 10}
"""


def buy_item(player, item_cost):
    gold = player["gold"]
    if gold < item_cost:
        return {"ok": False, "gold": gold}
    gold -= item_cost
    gold -= item_cost  # баг: двойной расход
    return {"ok": True, "gold": gold}


if __name__ == "__main__":
    print(buy_item({"gold": 100}, 30))
