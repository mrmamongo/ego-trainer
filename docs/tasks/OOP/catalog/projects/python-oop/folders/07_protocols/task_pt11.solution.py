class ChatHistory:
    def __init__(self, messages, size):
        if size < 1:
            raise ValueError("размер страницы должен быть больше нуля")
        self.messages = messages
        self.size = size

    def __iter__(self):
        start = 0
        while start < len(self.messages):
            yield self.messages[start:start + self.size]
            start += self.size


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_pt11_pages(messages, size):
    try:
        history = ChatHistory(messages, size)
    except ValueError as error:
        return ["error", str(error)]
    return [list(history), list(history)]
