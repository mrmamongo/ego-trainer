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

TEST_RUNS = [
    {"run_id": "r1", "model": "gpt-4o", "prompt": "Parse invoice #123"},
    {"run_id": "r2", "model": "claude-3", "prompt": "Summarize article"},
    {"run_id": "r3", "model": "gpt-3.5", "prompt": "Translate to Russian"},
    {"run_id": "r4", "model": "gpt-4o", "prompt": "Generate SQL query"},
]

TEST_CHUNKS = [
    {"run_id": "r1", "chunk_id": "c1", "text": "Found 3 line items"},
    {"run_id": "r1", "chunk_id": "c2", "text": "Total amount: $450"},
    {"run_id": "r2", "chunk_id": "c3", "text": "The article discusses..."},
    {"run_id": "r2", "chunk_id": "c4", "text": "Key findings include..."},
    {"run_id": "r2", "chunk_id": "c5", "text": "Conclusion: further research needed"},
    # r3 и r4 не имеют чанков
]

TEST_METRICS = [
    {"run_id": "r1", "tokens_in": 120, "tokens_out": 85},
    {"run_id": "r3", "tokens_in": 250, "tokens_out": 180},
    # r2 и r4 не имеют метрик
]


# =============================================================================
# ЭТАЛОННОЕ РЕШЕНИЕ
# =============================================================================

def _ref_merge_runs(runs, chunks, metrics):
    """Правильный ответ."""
    # Шаг 1: Индексируем чанки по run_id
    chunks_by_run = {}
    for c in chunks:
        rid = c["run_id"]
        if rid not in chunks_by_run:
            chunks_by_run[rid] = []
        # Кладём без run_id
        chunks_by_run[rid].append({
            "chunk_id": c["chunk_id"],
            "text": c["text"],
        })

    # Шаг 2: Индексируем метрики по run_id
    metrics_by_run = {}
    for m in metrics:
        rid = m["run_id"]
        metrics_by_run[rid] = {
            "tokens_in": m["tokens_in"],
            "tokens_out": m["tokens_out"],
        }

    # Шаг 3: Собираем итоговый словарь
    result = {}
    for r in runs:
        rid = r["run_id"]
        result[rid] = {
            "model": r["model"],
            "prompt": r["prompt"],
            "chunks": chunks_by_run.get(rid, []),
            "metrics": metrics_by_run.get(rid, {}),
        }

    return result


# =============================================================================
# ПРОВЕРКА
# =============================================================================

def main():
    print("=" * 50)
    print("  БЛОК A: Сборка из разных источников (join)")
    print("=" * 50)
    print()

    # Проверяем, что функция есть
    if not hasattr(student, "task_a_merge_runs"):
        print("❌ Функция task_a_merge_runs не найдена в student.py")
        sys.exit(1)

    # Вызываем функцию студента
    try:
        result = student.task_a_merge_runs(TEST_RUNS, TEST_CHUNKS, TEST_METRICS)
    except Exception as e:
        print(f"❌ Ошибка при выполнении task_a_merge_runs:")
        traceback.print_exc()
        sys.exit(1)

    # Сравниваем с эталоном
    expected = _ref_merge_runs(TEST_RUNS, TEST_CHUNKS, TEST_METRICS)

    if result == expected:
        print("✅ Задача A: task_a_merge_runs")
        print(f"   Собрано {len(result)} run'ов")
        for rid, data in result.items():
            chunks_count = len(data["chunks"])
            has_metrics = "да" if data["metrics"] else "нет"
            print(f"   {rid}: model={data['model']}, chunks={chunks_count}, metrics={has_metrics}")
        print()
        print("=" * 50)
        print("  🎉 Задача зачтена!")
        print("=" * 50)
    else:
        print("❌ Задача A: task_a_merge_runs")
        print()
        print("--- Ожидалось ---")
        import json
        print(json.dumps(expected, indent=2, ensure_ascii=False))
        print()
        print("--- Получилось ---")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print()
        print("=" * 50)
        print("  Попробуй исправить и запусти снова: python checker.py")
        print("=" * 50)


if __name__ == "__main__":
    main()
