class Cart:
    def __init__(self, items):
        self.items = items

    def __len__(self):
        return len(self.items)

    def __bool__(self):
        return any(price > 0 for _, price in self.items)


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mo16_cart(items):
    cart = Cart(items)
    label = "есть что оплатить" if cart else "нечего оплачивать"
    return [bool(cart), len(cart), label]
