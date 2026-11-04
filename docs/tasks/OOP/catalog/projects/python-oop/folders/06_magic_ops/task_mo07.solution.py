class Inventory:
    def __init__(self, items):
        self.items = items

    def __contains__(self, name):
        return self.items.get(name, 0) > 0


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mo07_has(items, names):
    inventory = Inventory(items)
    return [name in inventory for name in names]
