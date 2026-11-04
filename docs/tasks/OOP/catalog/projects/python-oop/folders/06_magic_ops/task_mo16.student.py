class Cart:
    def __init__(self, items):
        pass  # твой код: запомни items

    def __len__(self):
        pass  # твой код: верни число товаров

    def __bool__(self):
        pass  # твой код: True, если есть товар с ценой больше нуля


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mo16_cart(items):
    cart = Cart(items)
    label = "есть что оплатить" if cart else "нечего оплачивать"
    return [bool(cart), len(cart), label]
