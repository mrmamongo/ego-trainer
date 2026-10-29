from dataclasses import dataclass, asdict


@dataclass
class Message:
    author: str
    text: str
    likes: int = 0

    def to_dict(self):
        return asdict(self)


def task_dc14_popular(items, min_likes):
    popular = []
    for data in items:
        message = Message(data["author"], data["text"], data.get("likes", 0))
        if message.likes >= min_likes:
            popular.append(message)
    ordered = sorted(popular, key=lambda message: (-message.likes, message.author))
    return [message.to_dict() for message in ordered]
