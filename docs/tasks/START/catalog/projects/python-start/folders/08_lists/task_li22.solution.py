def task_li22_apply_discounts(prices, percent):
    return [round(price * (100 - percent) / 100, 2) for price in prices]
