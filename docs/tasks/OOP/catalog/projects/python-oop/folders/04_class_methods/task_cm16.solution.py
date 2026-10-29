class Price:
    def __init__(self, rubles):
        self.rubles = rubles

    @staticmethod
    def parse(text):
        return int(text.replace("руб", "").replace(" ", ""))

    @classmethod
    def from_text(cls, text):
        return cls(cls.parse(text))

    def show(self):
        return str(self.rubles) + " руб"


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_cm16_price(text):
    price = Price.from_text(text)
    return [Price.parse(text), price.rubles, price.show()]
