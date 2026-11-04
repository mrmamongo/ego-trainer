class Cart:
    def __init__(self, items):
        self.items = items

    def __len__(self):
        return len(self.items)

    def __getitem__(self, key):
        if isinstance(key, str):
            for name, price in self.items:
                if name == key:
                    return price
            raise KeyError(key)
        return self.items[key][0]


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mo17_cart(items, keys):
    cart = Cart(items)
    results = []
    for key in keys:
        try:
            results.append(cart[key])
        except (IndexError, KeyError, TypeError) as error:
            results.append(type(error).__name__)
    return results
