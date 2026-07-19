#!/usr/bin/env python3
"""
student.py — ТВОЙ файл. Пиши решения здесь.

5 задач в разных доменах. Уровень: циклы + словари + if.

Запуск проверки:
    python checker.py
"""


def task_d1_orders_by_category(orders):
    """
    D1. E-commerce: Выручка по категориям

    Аргументы:
        orders — список словарей:
        [{"id": "O1", "category": "electronics", "amount": 1200, "status": "paid"}, ...]

    Верни:
        Словарь: категория -> сумма amount ВСЕХ заказов (не только paid).
        Категории без заказов не попадают.

    Пример:
        >>> orders = [
        ...     {"category": "food", "amount": 100},
        ...     {"category": "food", "amount": 50},
        ...     {"category": "tech", "amount": 500},
        ... ]
        >>> task_d1_orders_by_category(orders)
        {"food": 150, "tech": 500}
    """
    pass


def task_d2_sensor_alerts(readings):
    """
    D2. IoT: Алёрты по сенсорам

    Аргументы:
        readings — список словарей:
        [{"sensor_id": "S1", "temperature": 85, "humidity": 40}, ...]

    Верни:
        Список sensor_id, где temperature > 80 ИЛИ humidity > 70.
        Без дубликатов. Порядок не важен.
    """
    pass


def task_d3_failed_builds(builds):
    """
    D3. CI/CD: Проваленные билды и их длительность

    Аргументы:
        builds — список словарей:
        [{"build_id": "B1", "status": "failed", "duration_sec": 45, "branch": "main"}, ...]

    Верни:
        Список словарей ТОЛЬКО для status == "failed", каждый с ключами:
        {"build_id": "...", "duration_sec": N, "branch": "..."}
        (ключ "status" убрать)
    """
    pass


def task_d4_inventory_value(inventory):
    """
    D4. Game: Стоимость инвентаря по редкости

    Аргументы:
        inventory — список словарей:
        [{"item": "Sword", "rarity": "rare", "qty": 2, "unit_price": 150}, ...]

    Верни:
        Словарь: rarity -> общая стоимость (qty * unit_price).
        rarity с маленькой буквы, как в данных.
    """
    pass


def task_d5_endpoint_stats(requests):
    """
    D5. API Gateway: Статистика по endpoint'ам

    Аргументы:
        requests — список словарей:
        [{"endpoint": "/api/users", "method": "GET", "status": 200, "ms": 45}, ...]

    Верни:
        Список словарей (по одному на endpoint):
        [
            {"endpoint": "/api/users", "count": 50, "avg_ms": 42},
            ...
        ]

        count = сколько запросов к endpoint
        avg_ms = среднее время ответа, округлённое до целого (round)

        Порядок: по алфавиту endpoint.
    """
    pass
