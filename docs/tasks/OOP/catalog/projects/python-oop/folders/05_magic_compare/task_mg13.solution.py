class Version:
    def __init__(self, text):
        self.text = text
        self.parts = [int(part) for part in text.split(".")]

    def __lt__(self, other):
        return self.parts < other.parts


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mg13_versions(texts):
    versions = [Version(text) for text in texts]
    newest = max(versions).text if versions else None
    return {"sorted": [version.text for version in sorted(versions)], "newest": newest}
