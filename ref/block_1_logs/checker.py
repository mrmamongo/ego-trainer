#!/usr/bin/env python3
"""
checker.py — ПРОВЕРЯЮЩИЙ скрипт. Ты его НЕ редактируешь, только запускаешь.

Как использовать:
    python checker.py

Что происходит:
    1. Генерирует тестовые логи (в памяти, файлы не нужны)
    2. Вызывает ТВОИ функции из student.py
    3. Сравнивает результат с правильным ответом
    4. Печатает: ✅ (зачёт) или ❌ (ошибка, с пояснением)

Если хочешь перегенерировать данные заново (случайные):
    python checker.py --random
"""

import sys
import traceback
import random
import json
from datetime import datetime, timedelta

# --- Импорт функций студента ---
try:
    import student
except Exception as e:
    print("❌ Не удалось импортировать student.py")
    print(f"   Ошибка: {e}")
    sys.exit(1)


# =============================================================================
# ГЕНЕРАТОР ТЕСТОВЫХ ДАННЫХ
# =============================================================================

SERVICES = ["api", "auth", "db", "payment", "notification"]

LEVEL_WEIGHTS = {"INFO": 70, "WARNING": 20, "ERROR": 10}

STATUS_POOL = (
    [200] * 60 + [201] * 15 + [301] * 5 + [400] * 8 +
    [401] * 4 + [403] * 3 + [404] * 4 + [500] * 1
)


def _generate_logs(count: int, seed: int, start: datetime) -> list[dict]:
    """Генерирует `count` лог-записей с фиксированным seed."""
    rng = random.Random(seed)
    logs = []
    for i in range(count):
        offset = timedelta(seconds=rng.randint(0, count))
        ts = (start + offset).isoformat()
        svc = rng.choice(SERVICES)
        status = rng.choice(STATUS_POOL)
        level = rng.choices(
            population=list(LEVEL_WEIGHTS.keys()),
            weights=list(LEVEL_WEIGHTS.values()),
        )[0]
        if level == "ERROR":
            status = rng.choice([500, 503, 502, 400, 401])
            rt = rng.randint(800, 3000)
        elif level == "WARNING":
            rt = rng.randint(300, 1500)
        else:
            rt = rng.randint(20, 400)
        logs.append({
            "timestamp": ts, "level": level, "service": svc,
            "status": status, "response_time_ms": rt,
        })
    return logs


def _inject_problems(logs: list[dict], start: datetime) -> list[dict]:
    """Добавляет гарантированные проблемные записи для small-набора."""
    problems = [
        {"timestamp": (start + timedelta(seconds=1)).isoformat(),
         "level": "ERROR", "service": "api", "status": 500, "response_time_ms": 1200},
        {"timestamp": (start + timedelta(seconds=2)).isoformat(),
         "level": "ERROR", "service": "auth", "status": 503, "response_time_ms": 2500},
        {"timestamp": (start + timedelta(seconds=3)).isoformat(),
         "level": "ERROR", "service": "api", "status": 500, "response_time_ms": 980},
        {"timestamp": (start + timedelta(seconds=4)).isoformat(),
         "level": "WARNING", "service": "db", "status": 200, "response_time_ms": 850},
        {"timestamp": (start + timedelta(seconds=5)).isoformat(),
         "level": "WARNING", "service": "payment", "status": 301, "response_time_ms": 720},
    ]
    combined = problems + logs
    combined.sort(key=lambda x: x["timestamp"])
    return combined


def make_datasets(random_seed: bool = False):
    """Создаёт small и medium наборы логов."""
    start = datetime(2026, 7, 10, 10, 0, 0)
    # Small: 15 случайных + 5 проблем = 20 записей
    small_random = _generate_logs(15, seed=42 if not random_seed else 123, start=start)
    small = _inject_problems(small_random, start)
    # Medium: 200 записей
    medium = _generate_logs(200, seed=43 if not random_seed else 124, start=start)
    return small, medium


# =============================================================================
# ЭТАЛОННЫЕ (ПРАВИЛЬНЫЕ) РЕШЕНИЯ
# =============================================================================

def _ref_1_1(logs):
    return sum(1 for e in logs if e["level"] == "ERROR")


def _ref_1_2(logs):
    d = {}
    for e in logs:
        if e["level"] == "ERROR":
            svc = e["service"]
            d[svc] = d.get(svc, 0) + 1
    return d


def _ref_1_3(logs):
    return [
        {"timestamp": e["timestamp"], "service": e["service"]}
        for e in logs if e["response_time_ms"] > 500
    ]


def _ref_1_4(logs):
    return list({e["service"] for e in logs if e["status"] == 500})


def _ref_1_5(logs):
    stats = {}
    for e in logs:
        svc = e["service"]
        if svc not in stats:
            stats[svc] = {"total": 0, "success": 0}
        stats[svc]["total"] += 1
        if 200 <= e["status"] <= 299:
            stats[svc]["success"] += 1
    report = []
    for svc, s in sorted(stats.items()):
        sla = round((s["success"] / s["total"]) * 100)
        report.append({
            "service": svc, "total": s["total"],
            "success": s["success"], "sla_percent": sla,
        })
    return report


# =============================================================================
# СИСТЕМА ПРОВЕРКИ
# =============================================================================

class CheckResult:
    def __init__(self, name: str, passed: bool, detail: str = ""):
        self.name = name
        self.passed = passed
        self.detail = detail


def _safe_call(func, args):
    """Вызывает функцию студента, ловит исключения."""
    try:
        return func(*args), None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def _format_for_display(obj, max_len: int = 200) -> str:
    """Форматирует объект для вывода, обрезая если длинный."""
    s = json.dumps(obj, ensure_ascii=False)
    if len(s) > max_len:
        s = s[:max_len] + "..."
    return s


def run_check(task_num: str, func_name: str, dataset, ref_func, note: str = ""):
    """Проверяет одну задачу. Возвращает CheckResult."""
    full_name = f"Задача {task_num}: {func_name}"

    # Проверяем, что функция есть в student.py
    if not hasattr(student, func_name):
        return CheckResult(full_name, False, f"Функция {func_name} не найдена в student.py")

    student_func = getattr(student, func_name)

    # Вызываем функцию студента
    result, error = _safe_call(student_func, (dataset,))
    if error:
        tb = traceback.format_exc()
        detail = f"Ошибка при выполнении:\n{tb}"
        return CheckResult(full_name, False, detail)

    # Сравниваем с эталоном
    expected = ref_func(dataset)

    if result == expected:
        msg = f"Результат: {_format_for_display(result)}"
        if note:
            msg += f"\n   Примечание: {note}"
        return CheckResult(full_name, True, msg)
    else:
        detail = (
            f"Ожидалось:  {_format_for_display(expected)}\n"
            f"Получилось: {_format_for_display(result)}"
        )
        return CheckResult(full_name, False, detail)


def main():
    use_random = "--random" in sys.argv

    print("=" * 60)
    print("  ПРОВЕРКА ЗАДАЧ БЛОКА 1: Инфраструктура / Логи")
    print("=" * 60)
    if use_random:
        print("  [Режим: случайные данные — ответы непредсказуемы]")
    else:
        print("  [Режим: фиксированные данные — ответы стабильны]")
    print()

    # Генерируем данные
    small, medium = make_datasets(random_seed=use_random)

    # Собираем проверки
    checks = [
        run_check("1.1", "task_1_1_count_errors", small, _ref_1_1,
                  note=f"набор: {len(small)} записей"),
        run_check("1.2", "task_1_2_errors_by_service", small, _ref_1_2,
                  note=f"набор: {len(small)} записей"),
        run_check("1.3", "task_1_3_slow_requests", small, _ref_1_3,
                  note=f"набор: {len(small)} записей"),
        run_check("1.4", "task_1_4_services_with_500", small, _ref_1_4,
                  note=f"набор: {len(small)} записей"),
        run_check("1.5", "task_1_5_sla_report", medium, _ref_1_5,
                  note=f"набор: {len(medium)} записей"),
    ]

    # Печатаем результаты
    passed = 0
    for check in checks:
        icon = "✅" if check.passed else "❌"
        print(f"{icon} {check.name}")
        for line in check.detail.split("\n"):
            print(f"   {line}")
        print()
        if check.passed:
            passed += 1

    # Итог
    print("=" * 60)
    total = len(checks)
    if passed == total:
        print(f"  🎉 Все {total}/{total} задач пройдены! Блок зачтён.")
    else:
        print(f"  Пройдено: {passed}/{total}. Попробуй исправить ❌ и запусти снова.")
    print("=" * 60)


if __name__ == "__main__":
    main()
