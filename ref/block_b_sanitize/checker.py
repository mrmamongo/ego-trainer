#!/usr/bin/env python3
"""
checker.py — ПРОВЕРЯЮЩИЙ скрипт. Не редактируй.

Запуск:
    python checker.py
"""

import sys
import traceback
import copy

# --- Импорт функций студента ---
try:
    import student
except Exception as e:
    print(f"❌ Не удалось импортировать student.py: {e}")
    sys.exit(1)


# =============================================================================
# ТЕСТОВЫЕ ДАННЫЕ (фиксированные)
# =============================================================================

TEST_PAYLOAD = {
    "run_id": "run_42",
    "agent": "InvoiceParser",
    "result": {
        "contact_email": "client@bigcorp.com",
        "items": [
            {
                "name": "Server",
                "supplier": {"name": "TechLtd", "email": "sales@techltd.io"},
                "price": 5000,
            },
            {
                "name": "License",
                "approved_by": "boss@company.com",
                "meta": {
                    "reviewer": "review@external.org",
                    "tags": ["critical", "urgent"],
                    "nested": {
                        "deep": {
                            "contact": "deep@inside.net",
                            "level": 3,
                        }
                    },
                },
            },
        ],
        "notes": "Contact us at support@helpdesk.ru or call +7-999-123-45-67",
        "metadata": {
            "created_by": "admin@system.local",
            "version": 2.1,
            "flags": ["processed", "verified"],
        },
    },
    "status": "done",
}

# Список всех email'ов, которые должны быть заменены
EMAILS_TO_REDACT = [
    "client@bigcorp.com",
    "sales@techltd.io",
    "boss@company.com",
    "review@external.org",
    "deep@inside.net",
    "support@helpdesk.ru",
    "admin@system.local",
]

# Ключи, которые НЕ должны измениться (не email'ы)
NON_EMAIL_STRINGS = [
    "InvoiceParser",      # agent
    "Server",             # items[0].name
    "TechLtd",            # items[0].supplier.name
    "License",            # items[1].name
    "critical",           # items[1].meta.tags[0]
    "urgent",             # items[1].meta.tags[1]
    "processed",          # result.metadata.flags[0]
    "verified",           # result.metadata.flags[1]
    "done",               # status
    "run_42",             # run_id
]


# =============================================================================
# ЭТАЛОННОЕ РЕШЕНИЕ
# =============================================================================

def _is_email(text):
    """Проверяет, является ли строка email-лайком."""
    return isinstance(text, str) and "@" in text and "." in text


def _ref_sanitize(payload):
    """Правильный ответ — рекурсивная санитизация."""
    if isinstance(payload, dict):
        return {
            key: _ref_sanitize(value)
            for key, value in payload.items()
        }
    elif isinstance(payload, list):
        return [_ref_sanitize(item) for item in payload]
    elif isinstance(payload, str) and _is_email(payload):
        return "<REDACTED>"
    else:
        return payload


# =============================================================================
# ПРОВЕРКА
# =============================================================================

def _check_no_emails(payload, path=""):
    """Рекурсивно проверяет, что ни одна строка не содержит email."""
    errors = []
    if isinstance(payload, dict):
        for k, v in payload.items():
            errors.extend(_check_no_emails(v, f"{path}.{k}"))
    elif isinstance(payload, list):
        for i, item in enumerate(payload):
            errors.extend(_check_no_emails(item, f"{path}[{i}]"))
    elif isinstance(payload, str) and _is_email(payload):
        errors.append(f"  Найден незамаскированный email: '{payload}' at {path}")
    return errors


def _check_preserved(payload, original, path=""):
    """Проверяет, что не-email строки и числа сохранились."""
    errors = []
    if isinstance(payload, dict):
        for k, v in payload.items():
            errors.extend(_check_preserved(v, original.get(k) if isinstance(original, dict) else None, f"{path}.{k}"))
    elif isinstance(payload, list):
        for i, item in enumerate(payload):
            orig_item = original[i] if isinstance(original, list) and i < len(original) else None
            errors.extend(_check_preserved(item, orig_item, f"{path}[{i}]"))
    elif isinstance(payload, str):
        if not _is_email(original) and payload != original:
            errors.append(f"  Изменена не-email строка: '{original}' → '{payload}' at {path}")
    elif isinstance(payload, (int, float)):
        if payload != original:
            errors.append(f"  Изменено число: {original} → {payload} at {path}")
    return errors


def main():
    print("=" * 50)
    print("  БЛОК B: Рекурсивная санитизация email'ов")
    print("=" * 50)
    print()

    # Проверяем, что функция есть
    if not hasattr(student, "task_b_sanitize"):
        print("❌ Функция task_b_sanitize не найдена в student.py")
        sys.exit(1)

    # Делаем копию, чтобы проверить, не мутировал ли оригинал
    original_copy = copy.deepcopy(TEST_PAYLOAD)

    # Вызываем функцию студента
    try:
        result = student.task_b_sanitize(TEST_PAYLOAD)
    except Exception as e:
        print(f"❌ Ошибка при выполнении task_b_sanitize:")
        traceback.print_exc()
        sys.exit(1)

    # Проверяем, что оригинал не мутировал (это допустимо, но проверим)
    # Важнее: проверяем результат

    errors = []

    # Проверка 1: Все email'ы замаскированы?
    email_errors = _check_no_emails(result)
    if email_errors:
        errors.append("Незамаскированные email'ы:")
        errors.extend(email_errors)

    # Проверка 2: Не-email строки и числа на месте?
    preserve_errors = _check_preserved(result, original_copy)
    if preserve_errors:
        errors.append("Изменены значения, которые не должны были меняться:")
        errors.extend(preserve_errors)

    # Проверка 3: Результат совпадает с эталоном?
    expected = _ref_sanitize(original_copy)
    if result != expected:
        # Детальное сравнение
        import json
        errors.append("Результат не совпадает с ожидаемым:")
        errors.append("--- Ожидалось (фрагмент) ---")
        exp_str = json.dumps(expected, indent=2, ensure_ascii=False)
        errors.append(exp_str[:800] + ("..." if len(exp_str) > 800 else ""))
        errors.append("--- Получилось (фрагмент) ---")
        res_str = json.dumps(result, indent=2, ensure_ascii=False)
        errors.append(res_str[:800] + ("..." if len(res_str) > 800 else ""))

    if not errors:
        print("✅ Задача B: task_b_sanitize")
        print(f"   Проверено {len(EMAILS_TO_REDACT)} email'ов — все замаскированы")
        print(f"   Проверено {len(NON_EMAIL_STRINGS)} не-email строк — все на месте")
        print(f"   Проверены числа — все на месте")
        print()
        print("=" * 50)
        print("  🎉 Задача зачтена!")
        print("=" * 50)
    else:
        print("❌ Задача B: task_b_sanitize")
        print()
        for err in errors:
            print(err)
        print()
        print("=" * 50)
        print("  Попробуй исправить и запусти снова: python checker.py")
        print("=" * 50)


if __name__ == "__main__":
    main()
