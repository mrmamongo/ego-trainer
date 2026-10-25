def given_capture(fn, *args):
    """GIVEN: вызвать fn(*args); вместо ошибки вернуть ["error", тип, сообщение]."""
    try:
        return fn(*args)
    except Exception as error:
        return ["error", type(error).__name__, str(error)]


def read_cents(text, default):
    try:
        rubles = int(text)
        return rubles * 100
    except ValueError:
        return default


def task_er04_cents(text, default):
    return given_capture(read_cents, text, default)
