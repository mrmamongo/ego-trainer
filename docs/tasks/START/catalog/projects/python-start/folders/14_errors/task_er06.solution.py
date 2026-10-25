def given_capture(fn, *args):
    """GIVEN: вызвать fn(*args); вместо ошибки вернуть ["error", тип, сообщение]."""
    try:
        return fn(*args)
    except Exception as error:
        return ["error", type(error).__name__, str(error)]


def parse_age(text):
    try:
        age = int(text)
    except ValueError:
        raise ValueError("не число")
    if age < 0:
        raise ValueError("меньше нуля")
    if age > 150:
        raise ValueError("больше 150")
    return age


def task_er06_age(text):
    return given_capture(parse_age, text)
