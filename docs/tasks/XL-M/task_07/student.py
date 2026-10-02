"""XL-M-07 — Исправь валидацию истории чата (баг: пропуск system).

Функция validate_history(history) проверяет, что в списке
сообщений нет пустых текстов и что role в допустимом наборе.
Текущая версия не проверяет пустые строки — пропускает их.

Верни {"ok": True} если всё ок, иначе {"ok": False,
"error": "<описание>"}.
Правила:
- Допустимые roles: "system", "user", "assistant"
- text не должен быть пустой строкой или пробелами
- Первое сообщение НЕ должно быть assistant (system/user OK)
- history может быть пустым (ok)

Пример:
    validate_history([{"role": "assistant", "text": "Hi"}])
    == {"ok": False, "error": "first message is assistant"}
"""


def validate_history(history):
    allowed = {"system", "user", "assistant"}
    for m in history:
        if m.get("role") not in allowed:
            return {"ok": False, "error": f"bad role {m.get('role')}"}
        if not m.get("text", "").strip():
            return {"ok": False, "error": "empty text"}
    return {"ok": True}


if __name__ == "__main__":
    print(validate_history([{"role": "assistant", "text": "Hi"}]))
