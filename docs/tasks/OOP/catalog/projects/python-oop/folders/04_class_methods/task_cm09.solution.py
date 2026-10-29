class Item:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["price"])


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_cm09_item(data):
    item = Item.from_dict(data)
    return [item.name, item.price]
