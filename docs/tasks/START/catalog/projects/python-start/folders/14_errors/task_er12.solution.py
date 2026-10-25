def task_er12_final_price(price, percent):
    # Собери тело функции из строк ниже. Они перемешаны и записаны без отступов:
    # порядок и отступы придётся расставить самому. Лишних строк нет.
    #
    #   return "percent_over_100"
    #   if price < 0:
    #   return price - price * percent // 100
    #   return "bad_price"
    #   if percent > 100:
    #   if percent < 0:
    #   return "percent_below_0"
    #
    if price < 0:
        return "bad_price"
    if percent < 0:
        return "percent_below_0"
    if percent > 100:
        return "percent_over_100"
    return price - price * percent // 100
