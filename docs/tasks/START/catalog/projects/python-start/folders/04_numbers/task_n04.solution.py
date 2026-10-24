def task_n04_parse_price(text):
    price = int(text)
    vat = price * 20 / 100
    return round(price + vat)
