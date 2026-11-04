class Inventory:
    def __init__(self, items):
        pass  # твой код: запомни словарь items

    def __getitem__(self, name):
        pass  # твой код: верни количество по названию

    def __contains__(self, name):
        pass  # твой код: верни True, если количество больше нуля

    def __len__(self):
        pass  # твой код: верни число названий


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mo15_inventory(items, names):
    inventory = Inventory(items)
    rows = []
    for name in names:
        try:
            count = inventory[name]
        except KeyError:
            count = "KeyError"
        rows.append([name, name in inventory, count])
    return {"kinds": len(inventory), "rows": rows}
