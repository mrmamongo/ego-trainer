def limit_three(func):
    def wrapper(*args):
        wrapper.calls = wrapper.calls + 1
        if wrapper.calls > 3:
            return None
        return func(*args)
    wrapper.calls = 0
    return wrapper


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def given_send(text):
    return "отправлено: " + text


def task_cm12_limit(first, second):
    send_one = limit_three(given_send)
    send_two = limit_three(given_send)
    return [[send_one(text) for text in first], [send_two(text) for text in second]]
