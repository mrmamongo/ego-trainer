class Inventory:
    def __init__(self, items):
        self.items = items

    def __getitem__(self, name):
        return self.items[name]

    def __contains__(self, name):
        return self.items.get(name, 0) > 0

    def __len__(self):
        return len(self.items)


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
