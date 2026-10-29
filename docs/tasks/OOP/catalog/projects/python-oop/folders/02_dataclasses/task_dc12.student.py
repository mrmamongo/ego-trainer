from dataclasses import dataclass


class Message:
    pass  # твой код: поля author, text, likes (по умолчанию 0) и метод to_dict


def message_from_dict(data):
    return None  # твой код


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_dc12_normalize(data):
    return message_from_dict(data).to_dict()
