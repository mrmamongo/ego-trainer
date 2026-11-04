class QuestLog:
    def __init__(self):
        self.titles = []

    def add(self, title):
        self.titles.append(title)

    def __iter__(self):
        return iter(self.titles)


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_pt05_quests(titles):
    log = QuestLog()
    for title in titles:
        log.add(title)
    return [list(log), list(log)]
