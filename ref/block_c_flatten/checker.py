#!/usr/bin/env python3
"""
checker.py — ПРОВЕРЯЮЩИЙ скрипт. Не редактируй.

Запуск:
    python checker.py
"""

import sys
import traceback

# --- Импорт функций студента ---
try:
    import student
except Exception as e:
    print(f"❌ Не удалось импортировать student.py: {e}")
    sys.exit(1)


# =============================================================================
# ТЕСТОВЫЕ ДАННЫЕ (фиксированные)
# =============================================================================

TEST_RUNS = {
    "run_1": {
        "model": "gpt-4o",
        "prompt": "Parse invoice #123 from Acme Corp",
        "chunks": [
            {"chunk_id": "ch_1", "text": "Invoice date: 2026-07-01", "timestamp": "2026-07-10T10:00:01"},
            {"chunk_id": "ch_2", "text": "Line items: 3 found", "timestamp": "2026-07-10T10:00:02"},
            {"chunk_id": "ch_3", "text": "Total amount: $1,250.00", "timestamp": "2026-07-10T10:00:03"},
        ],
    },
    "run_2": {
        "model": "claude-3-opus",
        "prompt": "Summarize quarterly report",
        "chunks": [
            {"chunk_id": "ch_4", "text": "Q2 revenue increased by 15%", "timestamp": "2026-07-10T10:01:01"},
        ],
    },
    "run_3": {
        "model": "gpt-3.5",
        "prompt": "Translate user manual",
        "chunks": [],  # пустые чанки — не должно быть строк
    },
    "run_4": {
        "model": "gpt-4o-mini",
        "prompt": "Generate test cases",
        "chunks": [
            {"chunk_id": "ch_5", "text": "Test login flow: valid credentials", "timestamp": "2026-07-10T10:02:01"},
            {"chunk_id": "ch_6", "text": "Test login flow: invalid password", "timestamp": "2026-07-10T10:02:02"},
            {"chunk_id": "ch_7", "text": "Test login flow: locked account", "timestamp": "2026-07-10T10:02:03", "extra": "has_retry"},
        ],
    },
}


# =============================================================================
# ЭТАЛОННОЕ РЕШЕНИЕ
# =============================================================================

def _ref_flatten(runs):
    """Правильный ответ."""
    result = []
    for run_id, run_data in runs.items():
        model = run_data["model"]
        for chunk in run_data.get("chunks", []):
            row = {
                "run_id": run_id,
                "model": model,
                "chunk_id": chunk["chunk_id"],
                "chunk_text": chunk["text"],
            }
            # Копируем остальные ключи из chunk (кроме text и chunk_id)
            for key, value in chunk.items():
                if key not in ("text", "chunk_id"):
                    row[key] = value
            result.append(row)
    return result


# =============================================================================
# ПРОВЕРКА
# =============================================================================

def main():
    print("=" * 50)
    print("  БЛОК C: Денормализация для фронта (flatten)")
    print("=" * 50)
    print()

    # Проверяем, что функция есть
    if not hasattr(student, "task_c_flatten"):
        print("❌ Функция task_c_flatten не найдена в student.py")
        sys.exit(1)

    # Вызываем функцию студента
    try:
        result = student.task_c_flatten(TEST_RUNS)
    except Exception as e:
        print(f"❌ Ошибка при выполнении task_c_flatten:")
        traceback.print_exc()
        sys.exit(1)

    # Проверяем, что результат не None
    if result is None:
        print("❌ Задача C: task_c_flatten")
        print()
        print("   Функция вернула None. Убедись, что используешь return.")
        print()
        print("=" * 50)
        print("  Попробуй исправить и запусти снова: python checker.py")
        print("=" * 50)
        return

    # Сравниваем с эталоном
    expected = _ref_flatten(TEST_RUNS)

    if result == expected:
        print("✅ Задача C: task_c_flatten")
        print(f"   Вход: {len(TEST_RUNS)} run'ов, {sum(len(r['chunks']) for r in TEST_RUNS.values())} chunks")
        print(f"   Выход: {len(result)} строк в плоской таблице")
        print()
        for row in result[:3]:
            print(f"   {row}")
        if len(result) > 3:
            print(f"   ... и ещё {len(result) - 3}")
        print()
        print("=" * 50)
        print("  🎉 Задача зачтена!")
        print("=" * 50)
    else:
        import json
        print("❌ Задача C: task_c_flatten")
        print()

        # Детальное сравнение
        if len(result) != len(expected):
            print(f"   Неверное количество строк: ожидалось {len(expected)}, получено {len(result)}")
            print()

        # Найдём первое расхождение
        for i, (exp, got) in enumerate(zip(expected, result)):
            if exp != got:
                print(f"   Первое расхождение в строке {i}:")
                print(f"   Ожидалось: {json.dumps(exp, ensure_ascii=False)}")
                print(f"   Получилось: {json.dumps(got, ensure_ascii=False)}")
                break
        else:
            if len(result) > len(expected):
                print(f"   Лишние строки: {result[len(expected):]}")
            elif len(result) < len(expected):
                print(f"   Недостающие строки: {expected[len(result):]}")

        print()
        print("--- Полный ожидаемый результат ---")
        print(json.dumps(expected, indent=2, ensure_ascii=False))
        print()
        print("--- Полный полученный результат ---")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print()
        print("=" * 50)
        print("  Попробуй исправить и запусти снова: python checker.py")
        print("=" * 50)


if __name__ == "__main__":
    main()
