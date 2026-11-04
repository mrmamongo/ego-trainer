import io
import json
from dataclasses import dataclass


@dataclass
class Profile:
    name: str
    level: int
    items: list

    def to_dict(self):
        return {"name": self.name, "level": self.level, "items": self.items}


def profile_from_dict(data):
    return Profile(data["name"], data["level"], data["items"])


def save_profile(profile, file):
    file.write(json.dumps(profile.to_dict(), ensure_ascii=False))


def load_profile(file):
    return profile_from_dict(json.loads(file.read()))


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_pt16_roundtrip(name, level, items):
    file = io.StringIO()
    save_profile(Profile(name, level, items), file)
    text = file.getvalue()
    file.seek(0)
    loaded = load_profile(file)
    return [text, loaded.name, loaded.level, loaded.items]
