"""XL-M-03 — Добавь поддержку system prompt в историю чата (правка).

Функция format_history(messages) принимает список сообщений и
возвращает строку для модели. Сейчас она поддерживает только user
и assistant, но игнорирует system-сообщения. System prompt должен
идти ПЕРВЫМ в формате "System: <text>", даже если в истории
system-сообщение не на первом месте.

Формат каждого сообщения: "<Role>: <text>" — разделитель ": ".
Если role не распознан — пропустить. Пустая история → пустая строка.

Пример:
    format_history([
        {"role": "user", "text": "Привет"},
        {"role": "system", "text": "Ты ассистент"},
        {"role": "assistant", "text": "Здравствуй"},
    ]) == "System: Ты ассистент\nUser: Привет\nAssistant: Здравствуй"
"""


def format_history(messages):
    role_prefix = {"system": "System", "user": "User", "assistant": "Assistant"}
    lines = []
    for m in messages:
        r = m.get("role")
        if r in role_prefix:
            lines.append(f"{role_prefix[r]}: {m['text']}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(repr(format_history([])))
