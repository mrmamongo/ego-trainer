class Price:
    def __init__(self, rubles):
        pass  # твой код

    @staticmethod
    def parse(text):
        return None  # твой код

    @classmethod
    def from_text(cls, text):
        return None  # твой код

    def show(self):
        return None  # твой код


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_cm16_price(text):
    price = Price.from_text(text)
    return [Price.parse(text), price.rubles, price.show()]
