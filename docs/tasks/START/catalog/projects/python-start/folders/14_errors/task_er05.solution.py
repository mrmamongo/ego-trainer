def task_er05_safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return "деление на ноль"
