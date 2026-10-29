from dataclasses import dataclass


@dataclass
class Message:
    author: str
    text: str
    likes: int = 0

    def to_dict(self):
        return {"author": self.author, "text": self.text, "likes": self.likes}


def message_from_dict(data):
    return Message(data["author"], data["text"], data.get("likes", 0))


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_dc12_normalize(data):
    return message_from_dict(data).to_dict()
