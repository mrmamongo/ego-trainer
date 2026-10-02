"""XL-O-16 — Память фактов с конфликтами (правка).

Расширь FactStore. Для каждого факта храни value, source, timestamp и
confidence. При записи конфликта актуальным становится факт с большей
confidence; при равенстве — более новый. Сохраняй history всех версий.
Реализуй put(key, value, source, timestamp, confidence), get(key) и
history(key). Не мутируй возвращаемые структуры.
"""

class FactStore:
    def __init__(self):
        self.current = {}
        self.versions = {}

    def put(self, key, value, source, timestamp, confidence):
        # TODO: реализовать выбор актуальной версии и историю
        raise NotImplementedError

    def get(self, key):
        return self.current.get(key)

    def history(self, key):
        return self.versions.get(key, [])
