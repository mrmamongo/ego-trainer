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
# ТЕСТОВЫЕ ДАННЫЕ
# =============================================================================

TEST_ORDERS = [
    {"id": "O1", "category": "electronics", "amount": 1200, "status": "paid"},
    {"id": "O2", "category": "food", "amount": 350, "status": "paid"},
    {"id": "O3", "category": "electronics", "amount": 800, "status": "cancelled"},
    {"id": "O4", "category": "clothing", "amount": 200, "status": "paid"},
    {"id": "O5", "category": "food", "amount": 120, "status": "pending"},
    {"id": "O6", "category": "electronics", "amount": 2500, "status": "paid"},
    {"id": "O7", "category": "books", "amount": 45, "status": "paid"},
]

TEST_READINGS = [
    {"sensor_id": "S1", "temperature": 72, "humidity": 35},
    {"sensor_id": "S2", "temperature": 92, "humidity": 40},
    {"sensor_id": "S3", "temperature": 68, "humidity": 75},
    {"sensor_id": "S4", "temperature": 85, "humidity": 80},
    {"sensor_id": "S2", "temperature": 88, "humidity": 45},  # S2 снова
    {"sensor_id": "S5", "temperature": 55, "humidity": 30},
]

TEST_BUILDS = [
    {"build_id": "B1", "status": "success", "duration_sec": 120, "branch": "main"},
    {"build_id": "B2", "status": "failed", "duration_sec": 45, "branch": "feature/auth"},
    {"build_id": "B3", "status": "success", "duration_sec": 90, "branch": "main"},
    {"build_id": "B4", "status": "failed", "duration_sec": 12, "branch": "hotfix/db"},
    {"build_id": "B5", "status": "failed", "duration_sec": 200, "branch": "feature/ui"},
    {"build_id": "B6", "status": "success", "duration_sec": 60, "branch": "main"},
]

TEST_INVENTORY = [
    {"item": "Iron Sword", "rarity": "common", "qty": 3, "unit_price": 50},
    {"item": "Dragon Scale", "rarity": "legendary", "qty": 1, "unit_price": 5000},
    {"item": "Health Potion", "rarity": "common", "qty": 10, "unit_price": 15},
    {"item": "Enchanted Bow", "rarity": "rare", "qty": 1, "unit_price": 300},
    {"item": "Gold Ring", "rarity": "rare", "qty": 2, "unit_price": 250},
    {"item": "Phoenix Feather", "rarity": "legendary", "qty": 1, "unit_price": 8000},
]

TEST_REQUESTS = [
    {"endpoint": "/api/users", "method": "GET", "status": 200, "ms": 45},
    {"endpoint": "/api/users", "method": "GET", "status": 200, "ms": 55},
    {"endpoint": "/api/users", "method": "POST", "status": 201, "ms": 120},
    {"endpoint": "/api/orders", "method": "GET", "status": 200, "ms": 30},
    {"endpoint": "/api/orders", "method": "GET", "status": 200, "ms": 25},
    {"endpoint": "/api/auth", "method": "POST", "status": 200, "ms": 80},
    {"endpoint": "/api/auth", "method": "POST", "status": 401, "ms": 15},
    {"endpoint": "/api/users", "method": "GET", "status": 200, "ms": 40},
    {"endpoint": "/api/health", "method": "GET", "status": 200, "ms": 5},
]


# =============================================================================
# ЭТАЛОННЫЕ РЕШЕНИЯ
# =============================================================================

def _ref_d1(orders):
    result = {}
    for o in orders:
        cat = o["category"]
        result[cat] = result.get(cat, 0) + o["amount"]
    return result


def _ref_d2(readings):
    alerts = set()
    for r in readings:
        if r["temperature"] > 80 or r["humidity"] > 70:
            alerts.add(r["sensor_id"])
    return list(alerts)


def _ref_d3(builds):
    return [
        {"build_id": b["build_id"], "duration_sec": b["duration_sec"], "branch": b["branch"]}
        for b in builds if b["status"] == "failed"
    ]


def _ref_d4(inventory):
    result = {}
    for item in inventory:
        rar = item["rarity"]
        value = item["qty"] * item["unit_price"]
        result[rar] = result.get(rar, 0) + value
    return result


def _ref_d5(requests):
    stats = {}
    for req in requests:
        ep = req["endpoint"]
        if ep not in stats:
            stats[ep] = {"total_ms": 0, "count": 0}
        stats[ep]["total_ms"] += req["ms"]
        stats[ep]["count"] += 1
    report = []
    for ep, s in sorted(stats.items()):
        report.append({
            "endpoint": ep,
            "count": s["count"],
            "avg_ms": round(s["total_ms"] / s["count"]),
        })
    return report


# =============================================================================
# ПРОВЕРКА
# =============================================================================

def run_check(task_num, func_name, dataset, ref_func, display_hint=""):
    """Проверяет одну задачу."""
    full_name = f"Задача {task_num}: {func_name}"

    if not hasattr(student, func_name):
        return (full_name, False, f"Функция {func_name} не найдена в student.py")

    try:
        result = getattr(student, func_name)(dataset)
    except Exception:
        tb = traceback.format_exc()
        return (full_name, False, f"Ошибка при выполнении:\n{tb}")

    if result is None:
        return (full_name, False, "Функция вернула None. Убедись, что используешь return.")

    expected = ref_func(dataset)

    # Для D2 сравниваем как множества (порядок не важен)
    if func_name == "task_d2_sensor_alerts":
        if set(result) == set(expected):
            return (full_name, True, f"Алёрты: {sorted(result)} {display_hint}")
        else:
            return (full_name, False, f"Ожидалось: {sorted(expected)}\nПолучилось: {sorted(result)}")

    if result == expected:
        import json
        return (full_name, True, f"Результат: {json.dumps(result, ensure_ascii=False)} {display_hint}")
    else:
        import json
        return (full_name, False,
                f"Ожидалось:  {json.dumps(expected, ensure_ascii=False)}\n"
                f"Получилось: {json.dumps(result, ensure_ascii=False)}")


def main():
    print("=" * 60)
    print("  БЛОК D: Разные домены (5 задач)")
    print("=" * 60)
    print()

    checks = [
        run_check("D1", "task_d1_orders_by_category", TEST_ORDERS, _ref_d1,
                  "(e-commerce: выручка по категориям)"),
        run_check("D2", "task_d2_sensor_alerts", TEST_READINGS, _ref_d2,
                  "(IoT: сенсоры с превышением порога)"),
        run_check("D3", "task_d3_failed_builds", TEST_BUILDS, _ref_d3,
                  "(CI/CD: проваленные билды)"),
        run_check("D4", "task_d4_inventory_value", TEST_INVENTORY, _ref_d4,
                  "(game: стоимость инвентаря)"),
        run_check("D5", "task_d5_endpoint_stats", TEST_REQUESTS, _ref_d5,
                  "(API gateway: статистика по endpoint'ам)"),
    ]

    passed = 0
    for name, ok, detail in checks:
        icon = "✅" if ok else "❌"
        print(f"{icon} {name}")
        for line in detail.split("\n"):
            print(f"   {line}")
        print()
        if ok:
            passed += 1

    print("=" * 60)
    if passed == len(checks):
        print(f"  🎉 Все {passed}/{len(checks)} задач пройдены!")
    else:
        print(f"  Пройдено: {passed}/{len(checks)}. Попробуй исправить ❌.")
    print("=" * 60)


if __name__ == "__main__":
    main()
