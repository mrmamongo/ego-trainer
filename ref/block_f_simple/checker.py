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

TEST_BUGS = [
    {"id": "B1", "severity": "minor", "title": "Typo in footer"},
    {"id": "B2", "severity": "major", "title": "Slow loading"},
    {"id": "B3", "severity": "critical", "title": "Crash on login"},
    {"id": "B4", "severity": "minor", "title": "Wrong icon"},
]

TEST_USERS = [
    {"name": "Ivan", "email": "ivan@test.com", "active": True},
    {"name": "Anna", "email": "anna@test.com", "active": False},
    {"name": "Boris", "email": "boris@test.com", "active": True},
    {"name": "Clara", "email": "clara@test.com", "active": False},
    {"name": "Dmitry", "email": "dmitry@test.com", "active": True},
]

TEST_TASKS = [
    {"id": "T1", "status": "done"},
    {"id": "T2", "status": "pending"},
    {"id": "T3", "status": "in_progress"},
    {"id": "T4", "status": "pending"},
    {"id": "T5", "status": "pending"},
    {"id": "T6", "status": "done"},
]

TEST_TESTS_ALL_PASS = [
    {"name": "test_login", "result": "passed"},
    {"name": "test_logout", "result": "passed"},
    {"name": "test_payment", "result": "passed"},
]

TEST_TESTS_ONE_FAIL = [
    {"name": "test_login", "result": "passed"},
    {"name": "test_cart", "result": "failed"},
    {"name": "test_payment", "result": "passed"},
]

TEST_ORDER_HAS_VIP = {
    "order_id": "O1",
    "items": [
        {"name": "Bread", "category": "food"},
        {"name": "Gold Watch", "category": "vip"},
        {"name": "Milk", "category": "food"},
    ],
}

TEST_ORDER_NO_VIP = {
    "order_id": "O2",
    "items": [
        {"name": "Pen", "category": "stationery"},
        {"name": "Notebook", "category": "stationery"},
    ],
}

TEST_ORDER_EMPTY = {
    "order_id": "O3",
    "items": [],
}


# =============================================================================
# ЭТАЛОННЫЕ РЕШЕНИЯ
# =============================================================================

def _ref_f1(bugs):
    for b in bugs:
        if b["severity"] == "critical":
            return b["title"]
    return ""


def _ref_f2(users):
    return [u["email"] for u in users if u["active"]]


def _ref_f3(tasks):
    count = 0
    for t in tasks:
        if t["status"] == "pending":
            count += 1
    return count


def _ref_f4(tests):
    for t in tests:
        if t["result"] != "passed":
            return False
    return True


def _ref_f5(order):
    for item in order.get("items", []):
        if item.get("category") == "vip":
            return True
    return False


# =============================================================================
# ПРОВЕРКА
# =============================================================================

def run_check(task_num, func_name, tests_cases):
    """
    tests_cases: список кортежей (input_data, expected, description)
    """
    full_name = f"Задача {task_num}: {func_name}"

    if not hasattr(student, func_name):
        return (full_name, False, f"Функция {func_name} не найдена в student.py")

    passed_cases = 0
    details = []

    for inp, expected, desc in tests_cases:
        try:
            result = getattr(student, func_name)(inp)
        except Exception:
            tb = traceback.format_exc()
            return (full_name, False, f"Ошибка в тесте '{desc}':\n{tb}")

        if result == expected:
            passed_cases += 1
            details.append(f"  ✅ {desc}: {result!r}")
        else:
            details.append(f"  ❌ {desc}: ожидалось {expected!r}, получено {result!r}")

    if passed_cases == len(tests_cases):
        return (full_name, True, "\n".join(details))
    else:
        return (full_name, False, "\n".join(details))


def main():
    print("=" * 60)
    print("  БЛОК F: Базовые паттерны (проще блока D)")
    print("=" * 60)
    print()

    checks = [
        run_check("F1", "task_f1_find_critical", [
            (TEST_BUGS, "Crash on login", "есть critical"),
            ([{"severity": "minor", "title": "Typo"}], "", "нет critical"),
            ([], "", "пустой список"),
        ]),
        run_check("F2", "task_f2_active_emails", [
            (TEST_USERS, ["ivan@test.com", "boris@test.com", "dmitry@test.com"], "3 из 5 активны"),
            ([{"email": "a@test", "active": False}], [], "нет активных"),
            ([], [], "пустой список"),
        ]),
        run_check("F3", "task_f3_count_pending", [
            (TEST_TASKS, 3, "3 pending из 6"),
            ([{"status": "done"}, {"status": "done"}], 0, "нет pending"),
            ([], 0, "пустой список"),
        ]),
        run_check("F4", "task_f4_all_passed", [
            (TEST_TESTS_ALL_PASS, True, "все passed"),
            (TEST_TESTS_ONE_FAIL, False, "один failed"),
            ([], True, "пустой список"),
        ]),
        run_check("F5", "task_f5_vip_in_order", [
            (TEST_ORDER_HAS_VIP, True, "есть VIP-товар"),
            (TEST_ORDER_NO_VIP, False, "нет VIP-товара"),
            (TEST_ORDER_EMPTY, False, "пустой заказ"),
        ]),
    ]

    passed = 0
    for name, ok, detail in checks:
        icon = "✅" if ok else "❌"
        print(f"{icon} {name}")
        print(detail)
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
