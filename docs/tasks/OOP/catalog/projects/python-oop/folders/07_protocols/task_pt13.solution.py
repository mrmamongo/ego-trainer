class Countdown:
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_pt13_countdown(start):
    timer = Countdown(start)
    first = list(timer)
    second = list(timer)
    other = Countdown(start)
    return [first, second, next(other, "конец"), next(other, "конец")]
