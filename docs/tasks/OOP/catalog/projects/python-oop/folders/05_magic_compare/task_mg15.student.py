class Message:
    def __init__(self, author, text):
        pass  # твой код: запомни author и text

    def __eq__(self, other):
        pass  # твой код: равны, если совпали автор и текст

    def __hash__(self):
        pass  # твой код: хеш от тех же полей


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mg15_dedupe(rows):
    messages = [Message(author, text) for author, text in rows]
    unique = list(dict.fromkeys(messages))
    return {
        "count": len(set(messages)),
        "first_seen": [[message.author, message.text] for message in unique],
    }
