"""XL-M-24 — Добавь торговлю между игроками (новый код).

Два игрока предлагают обмен.
trade(player_a, offer_a, player_b, offer_b):
- offer = {"items": [...], "gold": N}
- Проверь, что у каждого есть
  предложенные предметы и золото.
- Если кто-то не может заплатить
  — верни {"ok": False, "reason": ...}.
- Иначе переведи предметы+золото
  от одного к другому, верни
  {"ok": True}.
- Мутируй оба player dict'а.

Пример:
    a = {"items": ["sword"], "gold": 10}
    b = {"items": [], "gold": 5}
    trade(a, {"items": ["sword"], "gold": 0},
          b, {"items": [], "gold": 5})
    → a: {"items": [], "gold": 15}
    → b: {"items": ["sword"], "gold": 0}
"""


def trade(player_a, offer_a, player_b, offer_b):
    # TODO: реализовать обмен
    raise NotImplementedError


if __name__ == "__main__":
    a = {"items": ["sword"], "gold": 10}
    b = {"items": [], "gold": 5}
    print(trade(a, {"items": ["sword"], "gold": 0}, b, {"items": [], "gold": 5}))
