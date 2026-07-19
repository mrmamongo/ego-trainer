#!/usr/bin/env python3
"""
checker.py — ПРОВЕРЯЮЩИЙ скрипт. Не редактируй.

Запуск:
    python checker.py
"""

import sys
import traceback
import math

# --- Импорт функций студента ---
try:
    import student
except Exception as e:
    print(f"❌ Не удалось импортировать student.py: {e}")
    sys.exit(1)


# =============================================================================
# ЭТАЛОННЫЕ РЕШЕНИЯ
# =============================================================================

def _ref_g1(tokens):
    result = {}
    for t in tokens:
        if t not in result:
            result[t] = 0
        result[t] += 1
    return result


def _ref_g2(vocab, min_count):
    return {token: count for token, count in vocab.items() if count >= min_count}


def _ref_g3(tokens, max_len):
    return tokens[:max_len]


def _ref_g4(predicted, actual):
    if not predicted:
        return 0.0
    correct = sum(1 for p, a in zip(predicted, actual) if p == a)
    return correct / len(predicted)


def _ref_g5(sequences):
    result = {}
    for s in sequences:
        length = len(s["tokens"])
        if length not in result:
            result[length] = []
        result[length].append(s["id"])
    return result


def _ref_g6(sequences, pad_token):
    if not sequences:
        return {"padded": [], "attention_mask": []}
    max_len = max(len(seq) for seq in sequences)
    padded = []
    masks = []
    for seq in sequences:
        pad_count = max_len - len(seq)
        padded.append(seq + [pad_token] * pad_count)
        masks.append([1] * len(seq) + [0] * pad_count)
    return {"padded": padded, "attention_mask": masks}


def _ref_g7(logits, k):
    if not logits or k <= 0:
        return {token: float("-inf") for token in logits}
    sorted_values = sorted(logits.values(), reverse=True)
    threshold = sorted_values[min(k, len(sorted_values)) - 1]
    return {
        token: (value if value >= threshold else float("-inf"))
        for token, value in logits.items()
    }


# =============================================================================
# ТЕСТЫ
# =============================================================================

def _eq_float(a, b, eps=1e-6):
    return abs(a - b) < eps


def _eq_dict_floats(a, b):
    if set(a.keys()) != set(b.keys()):
        return False
    for k in a:
        if isinstance(a[k], float) and isinstance(b[k], float):
            if math.isinf(a[k]) and math.isinf(b[k]):
                continue
            if not _eq_float(a[k], b[k]):
                return False
        elif a[k] != b[k]:
            return False
    return True


def run_checks():
    checks = []

    # ===== G1 =====
    g1_tests = [
        (["the", "cat", "sat", "on", "the", "mat"], {"the": 2, "cat": 1, "sat": 1, "on": 1, "mat": 1}),
        (["a", "a", "a"], {"a": 3}),
        ([], {}),
    ]
    for inp, expected in g1_tests:
        result = student.task_g1_token_frequency(inp)
        if result == expected:
            checks.append(("G1", True, f"token_frequency({inp!r}) = {result}"))
        else:
            checks.append(("G1", False, f"Ожидалось: {expected}, Получилось: {result}"))

    # ===== G2 =====
    g2_tests = [
        ({"the": 50, "cat": 3, "xyz": 1}, 2, {"the": 50, "cat": 3}),
        ({"a": 1, "b": 2, "c": 3}, 5, {}),
        ({"hello": 10, "world": 10}, 10, {"hello": 10, "world": 10}),
    ]
    for vocab, min_c, expected in g2_tests:
        result = student.task_g2_vocab_filter(vocab, min_c)
        if result == expected:
            checks.append(("G2", True, f"vocab_filter(..., {min_c}) = {result}"))
        else:
            checks.append(("G2", False, f"Ожидалось: {expected}, Получилось: {result}"))

    # ===== G3 =====
    g3_tests = [
        ([101, 234, 456, 789, 102], 3, [101, 234, 456]),
        ([101, 234], 5, [101, 234]),
        ([], 3, []),
        ([1, 2, 3], 3, [1, 2, 3]),
    ]
    for tokens, ml, expected in g3_tests:
        result = student.task_g3_truncate_sequence(tokens, ml)
        if result == expected:
            checks.append(("G3", True, f"truncate({tokens!r}, {ml}) = {result}"))
        else:
            checks.append(("G3", False, f"Ожидалось: {expected}, Получилось: {result}"))

    # ===== G4 =====
    g4_tests = [
        ((["cat", "dog", "cat"], ["cat", "cat", "cat"]), 0.666667),
        ((["a", "b", "c"], ["a", "b", "c"]), 1.0),
        (([], []), 0.0),
        ((["x"], ["y"]), 0.0),
    ]
    for (pred, act), expected in g4_tests:
        result = student.task_g4_compute_accuracy(pred, act)
        if result is None:
            checks.append(("G4", False, f"Вернуло None. Забыл return?"))
            continue
        elif _eq_float(result, expected):
            checks.append(("G4", True, f"accuracy({pred!r}, {act!r}) = {result:.4f}"))
        else:
            checks.append(("G4", False, f"Ожидалось: ~{expected:.4f}, Получилось: {result}"))

    # ===== G5 =====
    g5_tests = [
        ([
            {"id": "s1", "tokens": [101, 234, 456]},
            {"id": "s2", "tokens": [101, 234]},
            {"id": "s3", "tokens": [101, 234, 456, 789]},
        ], {3: ["s1"], 2: ["s2"], 4: ["s3"]}),
        ([{"id": "a", "tokens": []}], {0: ["a"]}),
        ([], {}),
    ]
    for inp, expected in g5_tests:
        result = student.task_g5_group_by_length(inp)
        if result == expected:
            checks.append(("G5", True, f"group_by_length({len(inp)} seqs) = {result}"))
        else:
            checks.append(("G5", False, f"Ожидалось: {expected}, Получилось: {result}"))

    # ===== G6 =====
    g6_tests = [
        (
            [[101, 234, 456], [101, 234], [101, 234, 456, 789]],
            0,
            {
                "padded": [[101, 234, 456, 0], [101, 234, 0, 0], [101, 234, 456, 789]],
                "attention_mask": [[1, 1, 1, 0], [1, 1, 0, 0], [1, 1, 1, 1]],
            },
        ),
        (
            [[1, 2]],
            0,
            {"padded": [[1, 2]], "attention_mask": [[1, 1]]},
        ),
        (
            [],
            0,
            {"padded": [], "attention_mask": []},
        ),
    ]
    for seqs, pad, expected in g6_tests:
        result = student.task_g6_pad_batch(seqs, pad)
        if result == expected:
            checks.append(("G6", True, f"pad_batch({len(seqs)} seqs) OK"))
        else:
            checks.append(("G6", False, f"Ожидалось: {expected}, Получилось: {result}"))

    # ===== G7 =====
    g7_tests = [
        (
            {"cat": 2.5, "dog": 1.2, "bird": 0.1, "fish": 3.0, "mouse": -0.5},
            3,
            {"fish": 3.0, "cat": 2.5, "dog": 1.2, "bird": float("-inf"), "mouse": float("-inf")},
        ),
        (
            {"a": 1.0, "b": 2.0},
            5,
            {"a": 1.0, "b": 2.0},
        ),
        (
            {"x": 5.0, "y": 5.0, "z": 1.0},
            2,
            {"x": 5.0, "y": 5.0, "z": float("-inf")},
        ),
    ]
    for logits, k, expected in g7_tests:
        result = student.task_g7_top_k_filter(logits, k)
        if result is None:
            checks.append(("G7", False, f"Вернуло None. Забыл return?"))
            continue
        elif _eq_dict_floats(result, expected):
            checks.append(("G7", True, f"top_k_filter(..., {k}) OK"))
        else:
            checks.append(("G7", False, f"Ожидалось: {expected}, Получилось: {result}"))

    return checks


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 60)
    print("  БЛОК G: Первый день в лаборатории языковых моделей")
    print("=" * 60)
    print()

    # Проверяем наличие всех функций
    required = [
        "task_g1_token_frequency",
        "task_g2_vocab_filter",
        "task_g3_truncate_sequence",
        "task_g4_compute_accuracy",
        "task_g5_group_by_length",
        "task_g6_pad_batch",
        "task_g7_top_k_filter",
    ]
    missing = [f for f in required if not hasattr(student, f)]
    if missing:
        print(f"❌ Не найдены функции: {', '.join(missing)}")
        sys.exit(1)

    # Запускаем проверки
    try:
        checks = run_checks()
    except Exception:
        traceback.print_exc()
        sys.exit(1)

    # Группируем по задаче
    by_task = {}
    for task, ok, detail in checks:
        by_task.setdefault(task, []).append((ok, detail))

    passed_tasks = 0
    for task_name in sorted(by_task.keys()):
        task_checks = by_task[task_name]
        all_ok = all(ok for ok, _ in task_checks)
        icon = "✅" if all_ok else "❌"
        print(f"{icon} {task_name}")
        for ok, detail in task_checks:
            status = "✓" if ok else "✗"
            print(f"   {status} {detail}")
        print()
        if all_ok:
            passed_tasks += 1

    print("=" * 60)
    total = len(by_task)
    if passed_tasks == total:
        print(f"  🎉 Все {passed_tasks}/{total} задач пройдены!")
        print("  Можешь идти к старшему инженеру — покажет трансформер.")
    else:
        print(f"  Пройдено: {passed_tasks}/{total}. Попробуй исправить ❌.")
    print("=" * 60)


if __name__ == "__main__":
    main()
