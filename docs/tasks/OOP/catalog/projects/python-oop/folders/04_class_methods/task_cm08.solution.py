class Order:
    created = 0

    def __init__(self, product):
        self.product = product
        Order.created = Order.created + 1


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_cm08_orders(products):
    Order.created = 0  # каждая проверка начинается с нуля
    orders = [Order(product) for product in products]
    return [Order.created, [order.product for order in orders]]
