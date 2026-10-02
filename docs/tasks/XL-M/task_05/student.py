"""XL-M-05 — Нормализуй ответ модели для сравнения (правка).

При сравнении ответов модели нужно игнорировать регистр,
лишние пробелы и пунктуацию в конце. Реализуй
normalize_response(text):
- привести к lower()
- убрать пробелы по краям и внутри (заменить любой набор пробелов одним)
- убрать завершающие знаки препинания: . ! ? ...
- если после очистки строка пуста — вернуть ""

Примеры:
    normalize_response("  Hello, World!  ") == "hello, world"
    normalize_response("OK???") == "ok"
    normalize_response("  ...  ") == ""
"""

import re


def normalize_response(text):
    # Намеренная ошибка: не убирает точки и пробелы корректно
    text = text.strip().lower()
    return text


if __name__ == "__main__":
    print(normalize_response("  Hello, World!  "))
