# Задача B: Рекурсивная санитизация email'ов

**Блок:** B — Рекурсия
**Сложность:** hard
**Темы:** recursion, sanitize, email_redaction

## Условие

У тебя есть вложенный словарь — ответ от агента. Внутри могут быть email-адреса на ЛЮБОМ уровне вложенности. Нужно найти все email'ы и заменить их на строку `"<REDACTED>"`.

## Аргументы

- `payload` — вложенный словарь (dict), который может содержать:
  - строки (str)
  - числа (int, float)
  - списки (list)
  - другие словари (dict)

## Возвращает

Новый словарь (или изменённый оригинальный), где ЛЮБАЯ строка, содержащая символ `'@'` и точку `'.'` (email-лайк), заменена на `"<REDACTED>"`.

## Правила

- Проверяй ТОЛЬКО строки (`type(x) == str`)
- Строка считается email, если в ней ЕСТЬ `'@'` И `'.'`
- Списки и словари обходи рекурсивно
- Числа и другие типы не трогай
- Функция должна работать на ЛЮБОЙ глубине вложенности

## Пример

```python
# Вход:
{"name": "Ivan", "email": "ivan@test.com", "count": 42}

# Выход:
{"name": "Ivan", "email": "<REDACTED>", "count": 42}
```

<details>
<summary>Эталонное решение</summary>

```python
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
```

</details>
