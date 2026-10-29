def log_calls(func):
    def wrapper(*args):
        wrapper.log.append(list(args))
        return func(*args)
    wrapper.log = []


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def given_greet(name):
    return "Привет, " + name + "!"


def task_cm05_log(names):
    try:
        greet = log_calls(given_greet)
        results = [greet(name) for name in names]
        return [results, greet.log]
    except Exception as error:
        return ["error", type(error).__name__, str(error)]
