def task_fn17_part_of_day(hour):
    if hour <= 5:
        return "ночь"
    elif hour <= 11:
        return "утро"
    elif hour <= 17:
        return "день"
    else:
        return "вечер"
