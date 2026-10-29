def announce(func):
    def wrapper(*args):
        wrapper.calls = wrapper.calls + 1
        result = func(*args)
        wrapper.log.append(result)
        return result
    wrapper.log = []
    wrapper.calls = 0
    return wrapper


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def given_heal(hp, amount):
    return hp + amount


def task_cm18_calls(amounts):
    heal = announce(given_heal)
    results = [heal(10, amount) for amount in amounts]
    return [results, heal.log, getattr(heal, "calls", "нет атрибута calls")]
