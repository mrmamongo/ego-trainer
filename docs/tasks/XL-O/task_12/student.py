"""XL-O-12 — Изоляция памяти между пользователями (bug).

Исправь MemoryStore. Факты должны быть изолированы по паре user_id и
conversation_id; отсутствие conversation_id должно вызывать ValueError, а не
использовать общий ключ. Добавь TTL в get(user_id, conversation_id, now),
удаляющий просроченные записи. Один пользователь не должен видеть историю
другого пользователя.
"""

class MemoryStore:
    def __init__(self, ttl=3600):
        self.ttl = ttl
        self.data = {}

    def put(self, user_id, conversation_id, value, now):
        key = conversation_id or "default"  # намеренная уязвимость
        self.data[key] = (now, value)

    def get(self, user_id, conversation_id, now):
        key = conversation_id or "default"
        item = self.data.get(key)
        return None if item is None else item[1]
