class Countdown:
    def __init__(self, start):
        self.start = start

    def __iter__(self):
        n = self.start
        while n > 0:
            yield f"{n} сек"
            n -= 1


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_pt08_timer(start):
    timer = Countdown(start)
    return [list(timer), list(timer)]
