class QuestLog:
    def __init__(self):
        pass  # твой код

    def add(self, title):
        pass  # твой код

    def finish(self, title):
        pass  # твой код

    def __iter__(self):
        pass  # твой код


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
