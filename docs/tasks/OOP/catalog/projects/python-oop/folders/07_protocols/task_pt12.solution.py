class QuestLog:
    def __init__(self):
        self.titles = []
        self.done = set()

    def add(self, title):
        if title in self.titles:
            raise ValueError("квест уже есть")
        self.titles.append(title)

    def finish(self, title):
        if title not in self.titles:
            raise ValueError("нет такого квеста")
        self.done.add(title)

    def __iter__(self):
        for title in self.titles:
            if title not in self.done:
                yield title


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_pt12_quests(actions):
    log = QuestLog()
    results = []
    for name, title in actions:
        try:
            getattr(log, name)(title)
            results.append("ok")
        except ValueError as error:
            results.append(str(error))
    results.append(list(log))
    results.append(list(log))
    return results
