class ChatHistory:
    def __init__(self, messages, size):
        pass  # твой код: запомни messages и size, при size < 1 подними ValueError

    def __iter__(self):
        pass  # твой код: генератор страниц по size сообщений


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_pt11_pages(messages, size):
    try:
        history = ChatHistory(messages, size)
    except ValueError as error:
        return ["error", str(error)]
    return [list(history), list(history)]
