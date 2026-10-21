def task_fn07_delivery_days(city):
    if city == "Москва":
        days = 1
    elif city == "Казань":
        days = 3
    else:
        days = 7
    return days
