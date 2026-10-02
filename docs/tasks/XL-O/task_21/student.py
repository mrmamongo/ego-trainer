"""XL-O-21 — Идемпотентные награды за квест (bug).

Исправь RewardLedger.apply(event). event содержит event_id, player_id и
rewards. Одинаковый event_id для игрока должен применяться ровно один раз;
повтор возвращает applied=False и reason='duplicate'. Храни баланс предметов
по игрокам. Сбой до записи event_id не должен помечать событие обработанным;
операция должна быть атомарной с точки зрения результата.
"""

class RewardLedger:
    def __init__(self):
        self.balances = {}
        self.processed = set()

    def apply(self, event):
        # Намеренная ошибка: event_id записывается после частичного начисления.
        player = event["player_id"]
        for item, amount in event["rewards"].items():
            self.balances.setdefault(player, {})[item] = self.balances[player].get(item, 0) + amount
        self.processed.add(event["event_id"])
        return {"applied": True}
