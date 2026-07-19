#!/usr/bin/env python3
"""
Генератор JSONL-логов для практики (Блок 1: Инфраструктура / Логи)

Зачем: создаёт файлы с логами, на которых можно тренироваться решать
задачи по подсчёту ошибок, поиску медленных запросов, SLA-отчётам.

Что генерирует:
  - logs_small.jsonl   ~20 строк   (для задач 1.1, 1.2, 1.3, 1.4)
  - logs_medium.jsonl  ~200 строк  (для задачи 1.5 — SLA-отчёт)
  - logs_large.jsonl   ~2000 строк (для "погонять на скорость")

Как использовать:
    python generate_logs.py

Формат каждой строки (JSON):
    {
        "timestamp": "2026-07-10T10:00:01",
        "level": "INFO",
        "service": "api",
        "status": 200,
        "response_time_ms": 45
    }
"""

import json
import random
from datetime import datetime, timedelta

# --- Настройки ---

# Зафиксированный seed: при каждом запуске будут одинаковые логи.
# Это нужно, чтобы проверяющий (ты) знал правильные ответы.
random.seed(42)

SERVICES = ["api", "auth", "db", "payment", "notification"]

# Веса для уровней логирования (частота появления)
LEVEL_WEIGHTS = {
    "INFO": 70,
    "WARNING": 20,
    "ERROR": 10,
}

# HTTP-статусы и их вероятность
STATUS_POOL = (
    [200] * 60
    + [201] * 15
    + [301] * 5
    + [400] * 8
    + [401] * 4
    + [403] * 3
    + [404] * 4
    + [500] * 1
)


def random_timestamp(start: datetime, n: int) -> str:
    """Генерирует timestamp, равномерно распределённый от start до start + n секунд."""
    offset = timedelta(seconds=random.randint(0, n))
    return (start + offset).isoformat()


def generate_log_entry(timestamp: str) -> dict:
    """Создаёт одну запись лога со случайными, но реалистичными данными."""
    service = random.choice(SERVICES)
    status = random.choice(STATUS_POOL)

    # У ERROR-ов чаще высокий response_time и всегда status >= 400
    level = random.choices(
        population=list(LEVEL_WEIGHTS.keys()),
        weights=list(LEVEL_WEIGHTS.values()),
    )[0]

    if level == "ERROR":
        status = random.choice([500, 503, 502, 400, 401])
        response_time = random.randint(800, 3000)
    elif level == "WARNING":
        response_time = random.randint(300, 1500)
    else:
        response_time = random.randint(20, 400)

    return {
        "timestamp": timestamp,
        "level": level,
        "service": service,
        "status": status,
        "response_time_ms": response_time,
    }


def generate_logs(count: int, start_time: datetime) -> list[dict]:
    """Генерирует список из `count` лог-записей."""
    logs = []
    for i in range(count):
        ts = random_timestamp(start_time, count)
        logs.append(generate_log_entry(ts))
    return logs


def save_jsonl(logs: list[dict], filename: str) -> None:
    """Сохраняет логи в файл: каждая строка — один JSON-объект."""
    with open(filename, "w", encoding="utf-8") as f:
        for entry in logs:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"  Сохранено {len(logs)} записей → {filename}")


def print_preview(logs: list[dict], n: int = 3) -> None:
    """Показывает первые n записей для проверки."""
    for entry in logs[:n]:
        print("   ", json.dumps(entry, ensure_ascii=False))
    if len(logs) > n:
        print(f"   ... и ещё {len(logs) - n} записей")


def print_answers_small(logs: list[dict]) -> None:
    """
    Печатает правильные ответы для маленького набора.
    Используй для самопроверки или чтобы подсказать, если друг застрял.
    """
    print("\n--- Правильные ответы (logs_small.jsonl) ---")

    # 1.1
    error_count = sum(1 for e in logs if e["level"] == "ERROR")
    print(f"1.1 Всего ERROR: {error_count}")

    # 1.2
    errors_by_service = {}
    for e in logs:
        if e["level"] == "ERROR":
            svc = e["service"]
            errors_by_service[svc] = errors_by_service.get(svc, 0) + 1
    print(f"1.2 Ошибки по сервисам: {errors_by_service}")

    # 1.3
    slow = [{"timestamp": e["timestamp"], "service": e["service"]}
            for e in logs if e["response_time_ms"] > 500]
    print(f"1.3 Медленные запросы (>500ms): {len(slow)} шт.")
    for s in slow:
        print(f"     {s}")

    # 1.4
    services_with_500 = list({e["service"] for e in logs if e["status"] == 500})
    print(f"1.4 Сервисы с 500-ми: {services_with_500}")


def print_answers_medium(logs: list[dict]) -> None:
    """Печатает правильный SLA-отчёт для среднего набора (задача 1.5)."""
    print("\n--- Правильный SLA-отчёт (logs_medium.jsonl, задача 1.5) ---")

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
            "service": svc,
            "total": s["total"],
            "success": s["success"],
            "sla_percent": sla,
        })
        print(f"  {svc}: total={s['total']}, success={s['success']}, sla={sla}%")


def inject_problems(logs: list[dict], start_time: datetime) -> list[dict]:
    """
    Добавляет гарантированные "проблемные" записи в лог.
    Нужно, чтобы в small-наборе точно были ERROR, 500-е и медленные запросы.
    Иначе задачи 1.1–1.4 теряют смысл.
    """
    problems = [
        {
            "timestamp": (start_time + timedelta(seconds=1)).isoformat(),
            "level": "ERROR",
            "service": "api",
            "status": 500,
            "response_time_ms": 1200,
        },
        {
            "timestamp": (start_time + timedelta(seconds=2)).isoformat(),
            "level": "ERROR",
            "service": "auth",
            "status": 503,
            "response_time_ms": 2500,
        },
        {
            "timestamp": (start_time + timedelta(seconds=3)).isoformat(),
            "level": "ERROR",
            "service": "api",
            "status": 500,
            "response_time_ms": 980,
        },
        {
            "timestamp": (start_time + timedelta(seconds=4)).isoformat(),
            "level": "WARNING",
            "service": "db",
            "status": 200,
            "response_time_ms": 850,
        },
        {
            "timestamp": (start_time + timedelta(seconds=5)).isoformat(),
            "level": "WARNING",
            "service": "payment",
            "status": 301,
            "response_time_ms": 720,
        },
    ]
    # Перемешиваем проблемные записи со случайными
    combined = problems + logs
    # Сортируем по timestamp, чтобы выглядело реалистично
    combined.sort(key=lambda x: x["timestamp"])
    return combined


def main():
    print("=" * 50)
    print("Генератор логов для практики")
    print("=" * 50)

    start_time = datetime(2026, 7, 10, 10, 0, 0)

    # --- Small: для задач 1.1–1.4 ---
    # 15 случайных + 5 гарантированных проблем = 20 записей
    print("\n[1/3] Генерация logs_small.jsonl (20 записей: 15 случайных + 5 проблем)")
    logs_small = generate_logs(15, start_time)
    logs_small = inject_problems(logs_small, start_time)
    print_preview(logs_small)
    save_jsonl(logs_small, "logs_small.jsonl")
    print_answers_small(logs_small)

    # --- Medium: для задачи 1.5 (SLA-отчёт) ---
    print("\n[2/3] Генерация logs_medium.jsonl (~200 записей)")
    logs_medium = generate_logs(200, start_time)
    print_preview(logs_medium)
    save_jsonl(logs_medium, "logs_medium.jsonl")
    print_answers_medium(logs_medium)

    # --- Large: для нагрузочной практики ---
    print("\n[3/3] Генерация logs_large.jsonl (~2000 записей)")
    logs_large = generate_logs(2000, start_time)
    print_preview(logs_large)
    save_jsonl(logs_large, "logs_large.jsonl")
    print("  (для этого набора считай ответы самостоятельно)")

    print("\n" + "=" * 50)
    print("Готово! Все файлы созданы в текущей папке.")
    print("Запускай скрипты друга и сверяй с ответами выше.")
    print("=" * 50)


if __name__ == "__main__":
    main()
