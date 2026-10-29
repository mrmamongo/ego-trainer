from dataclasses import dataclass


@dataclass
class Message:
    # поля: author, text, likes (по умолчанию 0)

    def to_dict(self):
        pass  # твой код


def message_from_dict(data):
    return None  # твой код


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_dc12_normalize(data):
    return message_from_dict(data).to_dict()
