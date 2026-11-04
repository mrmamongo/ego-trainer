class QuestLog:
    def __init__(self):
        self.titles = []
        self.pos = 0

    def add(self, title):
        self.titles.append(title)

    def __iter__(self):
        return self

    def __next__(self):
        if self.pos >= len(self.titles):
            raise StopIteration
        title = self.titles[self.pos]
        self.pos += 1
        return title


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_pt05_quests(titles):
    log = QuestLog()
    for title in titles:
        log.add(title)
    return [list(log), list(log)]
