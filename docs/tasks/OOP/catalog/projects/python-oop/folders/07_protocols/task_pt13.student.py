class Countdown:
    def __init__(self, start):
        pass  # твой код

    def __iter__(self):
        pass  # твой код

    def __next__(self):
        pass  # твой код


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_pt13_countdown(start):
    timer = Countdown(start)
    first = list(timer)
    second = list(timer)
    other = Countdown(start)
    return [first, second, next(other, "конец"), next(other, "конец")]
