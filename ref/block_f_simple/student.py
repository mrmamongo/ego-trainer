#!/usr/bin/env python3
"""
student.py — ТВОЙ файл. Пиши решения здесь.

5 простых задач на базовые паттерны. Уровень: проще блока D.

Запуск проверки:
    python checker.py
"""


def task_f1_find_critical(bugs):
    """
    F1. Bug tracker: Найди первый критический баг

    Аргументы:
        bugs — список словарей:
        [{"id": "B1", "severity": "critical", "title": "Crash on login"}, ...]

    Верни:
        Значение поля "title" первого бага с severity == "critical".
        Если такого нет — верни пустую строку "".
    """
    pass


def task_f2_active_emails(users):
    """
    F2. CRM: Email'ы активных пользователей

    Аргументы:
        users — список словарей:
        [{"name": "Ivan", "email": "ivan@test.com", "active": True}, ...]

    Верни:
        Список email'ов (строк) только тех, у кого active == True.
        Порядок: как во входном списке.
    """
    pass


def task_f3_count_pending(tasks):
    """
    F3. Task tracker: Сколько задач в статусе "pending"?

    Аргументы:
        tasks — список словарей:
        [{"id": "T1", "status": "pending"}, ...]

    Верни:
        Число — сколько записей с status == "pending".
    """
    pass


def task_f4_all_passed(tests):
    """
    F4. CI/CD: Все ли тесты пройдены?

    Аргументы:
        tests — список словарей:
        [{"name": "test_login", "result": "passed"}, ...]

    Верни:
        True — если ВСЕ тесты имеют result == "passed".
        False — если хотя бы один не "passed".
        Если список пустой — верни True.
    """
    pass


def task_f5_vip_in_order(order):
    """
    F5. E-commerce: Есть ли VIP-товар в заказе?

    Аргументы:
        order — ОДИН словарь (не список!):
        {"order_id": "O1", "items": [
            {"name": "Pen", "category": "stationery"},
            {"name": "Watch", "category": "vip"},
        ]}

    Верни:
        True — если хотя бы один item имеет category == "vip".
        False — если нет.
        Если items пустой — верни False.
    """
    pass
