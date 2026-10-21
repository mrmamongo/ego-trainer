def task_fn12_final_price(price, is_member):
    if is_member:
        price = price - price // 10
    if price > 5000:
        price = price - 500
    return price
