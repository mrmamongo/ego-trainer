#!/usr/bin/env python3
"""
Эталонные решения задач Блока 1 (Инфраструктура / Логи)

Что делает:
    Читает JSONL-файл с логами и решает задачи 1.1 – 1.5,
    распечатывая результаты.

Как использовать:
    # Для small-логов (задачи 1.1–1.4)
    python solutions_block1.py logs_small.jsonl

    # Для medium-логов (задача 1.5 — SLA-отчёт)
    python solutions_block1.py logs_medium.jsonl --sla

    # Для large-логов (проверь себя сам)
    python solutions_block1.py logs_large.jsonl --all
"""

import json
import sys


def load_logs(filepath: str) -> list[dict]:
    """
    Читает JSONL-файл: каждая строка — отдельный JSON-объект.
    Возвращает список словарей.
    """
    logs = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:  # пропускаем пустые строки
                logs.append(json.loads(line))
    return logs


def task_1_1_count_errors(logs: list[dict]) -> int:
    """
    Задача 1.1: Подсчёт ошибок
    Посчитай, сколько всего записей с level == "ERROR".
    """
    count = 0
    for entry in logs:
        if entry["level"] == "ERROR":
            count += 1
    return count


def task_1_2_errors_by_service(logs: list[dict]) -> dict:
    """
    Задача 1.2: Кто болеет?
    Посчитай, сколько ошибок (level == "ERROR") пришло от каждого service.
    Верни словарь: {"api": 2, "auth": 5, ...}
    """
    result = {}
    for entry in logs:
        if entry["level"] == "ERROR":
            service = entry["service"]
            # .get(key, 0) — берёт текущее значение или 0, если ключа ещё нет
            result[service] = result.get(service, 0) + 1
    return result


def task_1_3_slow_requests(logs: list[dict]) -> list[dict]:
    """
    Задача 1.3: Медленные запросы
    Найди все записи, где response_time_ms > 500.
    Собери их в список, но оставь только timestamp и service.
    """
    result = []
    for entry in logs:
        if entry["response_time_ms"] > 500:
            filtered = {
                "timestamp": entry["timestamp"],
                "service": entry["service"],
            }
            result.append(filtered)
    return result


def task_1_4_services_with_500(logs: list[dict]) -> list[str]:
    """
    Задача 1.4: Алёрт на 500-е
    Найди все уникальные service, которые хотя бы раз вернули status == 500.
    Верни список имён без дубликатов.

    Почему set: потому что один сервис мог сломаться несколько раз,
    а нам нужны только уникальные имена.
    """
    services = set()
    for entry in logs:
        if entry["status"] == 500:
            services.add(entry["service"])
    return list(services)


def task_1_5_sla_report(logs: list[dict]) -> list[dict]:
    """
    Задача 1.5: SLA-отчёт
    Для каждого service посчитай:
      - сколько всего запросов
      - сколько успешных (status 200–299)
      - процент успешных (округли до целого)

    Логика:
      1. Собираем статистику во временный словарь
      2. Преобразуем в итоговый список словарей
    """
    # Временный словарь: service -> {"total": N, "success": M}
    stats = {}

    for entry in logs:
        service = entry["service"]

        # Если сервис встретился первый раз — создаём для него запись
        if service not in stats:
            stats[service] = {"total": 0, "success": 0}

        stats[service]["total"] += 1

        # Успешные статусы: 200, 201, 202, ... 299
        if 200 <= entry["status"] <= 299:
            stats[service]["success"] += 1

    # Преобразуем словарь в список отчётов
    report = []
    for service, data in sorted(stats.items()):
        sla_percent = round((data["success"] / data["total"]) * 100)
        report.append({
            "service": service,
            "total": data["total"],
            "success": data["success"],
            "sla_percent": sla_percent,
        })

    return report


def main():
    # --- Разбор аргументов командной строки ---
    if len(sys.argv) < 2:
        print("Usage: python solutions_block1.py <file.jsonl> [--sla | --all]")
        print("  --sla   показать только SLA-отчёт (задача 1.5)")
        print("  --all   показать все задачи")
        sys.exit(1)

    filepath = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "--all"

    # --- Загрузка данных ---
    print(f"Читаем: {filepath}")
    logs = load_logs(filepath)
    print(f"Загружено записей: {len(logs)}\n")

    # --- Решения ---
    if mode in ("--all",):
        print("=" * 40)
        print("Задача 1.1: Подсчёт ошибок")
        print("=" * 40)
        error_count = task_1_1_count_errors(logs)
        print(f"Всего ERROR: {error_count}\n")

        print("=" * 40)
        print("Задача 1.2: Кто болеет? (ошибки по сервисам)")
        print("=" * 40)
        errors_by_svc = task_1_2_errors_by_service(logs)
        print(f"Результат: {json.dumps(errors_by_svc, ensure_ascii=False)}\n")

        print("=" * 40)
        print("Задача 1.3: Медленные запросы (>500ms)")
        print("=" * 40)
        slow = task_1_3_slow_requests(logs)
        print(f"Найдено: {len(slow)}")
        for entry in slow:
            print(f"  {entry}")
        print()

        print("=" * 40)
        print("Задача 1.4: Сервисы с 500-ми статусами")
        print("=" * 40)
        svc_500 = task_1_4_services_with_500(logs)
        print(f"Результат: {svc_500}\n")

    if mode in ("--all", "--sla"):
        print("=" * 40)
        print("Задача 1.5: SLA-отчёт")
        print("=" * 40)
        report = task_1_5_sla_report(logs)
        for row in report:
            print(f"  {row['service']}: "
                  f"total={row['total']}, "
                  f"success={row['success']}, "
                  f"sla={row['sla_percent']}%")
        print()


if __name__ == "__main__":
    main()
