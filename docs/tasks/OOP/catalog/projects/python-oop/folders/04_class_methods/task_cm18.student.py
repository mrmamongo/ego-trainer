# Сейчас декоратор записывает в журнал wrapper.log результаты вызовов.
def announce(func):
    def wrapper(*args):
        result = func(*args)
        wrapper.log.append(result)
        return result
    wrapper.log = []
    return wrapper


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def given_heal(hp, amount):
    return hp + amount


def task_cm18_calls(amounts):
    heal = announce(given_heal)
    results = [heal(10, amount) for amount in amounts]
    return [results, heal.log, getattr(heal, "calls", "нет атрибута calls")]
