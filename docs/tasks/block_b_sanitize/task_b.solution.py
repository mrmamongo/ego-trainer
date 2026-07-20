def _is_email(text):
    """Проверяет, является ли строка email-лайком."""
    return isinstance(text, str) and "@" in text and "." in text


def task_b_sanitize(payload):
    """Правильный ответ — рекурсивная санитизация."""
    if isinstance(payload, dict):
        return {
            key: task_b_sanitize(value)
            for key, value in payload.items()
        }
    elif isinstance(payload, list):
        return [task_b_sanitize(item) for item in payload]
    elif isinstance(payload, str) and _is_email(payload):
        return "<REDACTED>"
    else:
        return payload
