class Message:
    def __init__(self, author, text):
        self.author = author
        self.text = text

    def __eq__(self, other):
        if not isinstance(other, Message):
            return NotImplemented
        return self.author == other.author and self.text == other.text

    def __hash__(self):
        return hash((self.author, self.text))


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mg06_unique(rows):
    messages = [Message(author, text) for author, text in rows]
    return given_count(messages)


def given_count(messages):
    """Готовый помощник: сколько разных сообщений в множестве; если их нельзя положить в множество, вернёт «TypeError»."""
    try:
        return len(set(messages))
    except TypeError:
        return "TypeError"
