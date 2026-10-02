"""XL-M-22 — Реализуй шаг dungeon (правка).

Dungeon — список комнат. Каждая комната
{"id": ..., "exits": {"north": id, ...},
 "loot": [...]}. Игрок в "current":
{"room": id, "inventory": [...]}.

Функция dungeon_step(state, direction):
- Найди текущую комнату по id.
- Если direction нет в exits — верни
  {"ok": False, "reason": "no exit"}
- Иначе перемести игрока, добавь
  loot комнаты в inventory,
  очисти loot комнаты (пустой список).
- Верните {"ok": True, "room": new_id,
  "loot_collected": [...]}.

Пример:
    state = {"room": "r1", "inventory": []}
    dungeon = [{"id":"r1","exits":{"north":"r2"},"loot":["sword"]}]
    dungeon_step(state, "north")
    → {"ok": True, "room": "r2", "loot_collected": ["sword"]}
"""


def dungeon_step(state, direction, dungeon):
    # TODO: реализовать шаг по dungeon
    raise NotImplementedError


if __name__ == "__main__":
    state = {"room": "r1", "inventory": []}
    dungeon = [{"id": "r1", "exits": {"north": "r2"}, "loot": ["sword"]}]
    print(dungeon_step(state, "north", dungeon))
