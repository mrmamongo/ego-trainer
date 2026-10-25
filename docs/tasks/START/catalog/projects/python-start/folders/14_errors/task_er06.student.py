def given_capture(fn, *args):
    """GIVEN: вызвать fn(*args); вместо ошибки вернуть ["error", тип, сообщение]."""
    try:
        return fn(*args)
    except Exception as error:
        return ["error", type(error).__name__, str(error)]


def parse_age(text):
    # Верни возраст (целое число) или брось ValueError с сообщением:
    # "не число", "меньше нуля" или "больше 150".
    return None


def task_er06_age(text):
    return given_capture(parse_age, text)
