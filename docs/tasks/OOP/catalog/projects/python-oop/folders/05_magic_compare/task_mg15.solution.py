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

def task_mg15_dedupe(rows):
    messages = [Message(author, text) for author, text in rows]
    unique = list(dict.fromkeys(messages))
    return {
        "count": len(set(messages)),
        "first_seen": [[message.author, message.text] for message in unique],
    }
