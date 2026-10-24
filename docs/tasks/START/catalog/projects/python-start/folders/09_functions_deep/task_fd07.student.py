# Сейчас функция работает по старому правилу: всегда НДС 20%.
def task_fd07_price_with_vat(price):
    return price + price * 20 // 100
