def task_fd07_price_with_vat(price, rate=20):
    return price + price * rate // 100
