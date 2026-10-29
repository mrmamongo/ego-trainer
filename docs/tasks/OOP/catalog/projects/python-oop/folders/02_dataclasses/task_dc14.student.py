from dataclasses import dataclass, asdict


@dataclass
class Message:
    author: str
    text: str
    likes: int = 0

    def to_dict(self):
        return asdict(self)


def task_dc14_popular(items, min_likes):
    return None  # твой код
