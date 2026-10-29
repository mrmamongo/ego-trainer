class Quest:
    def __init__(self, title, reward):
        self.title = title
        self.reward = reward

    @classmethod
    def from_dict(cls, data):
        return cls(data["title"], data.get("reward", 0))

    @classmethod
    def from_string(cls, text):
        parts = text.split(":")
        reward = 0
        if len(parts) > 1:
            reward = int(parts[1])
        return cls(parts[0], reward)


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_cm17_quest(kind, value):
    if kind == "dict":
        quest = Quest.from_dict(value)
    else:
        quest = Quest.from_string(value)
    return [quest.title, quest.reward]
