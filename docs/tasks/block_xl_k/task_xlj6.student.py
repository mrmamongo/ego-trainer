"""Задача J6: Retry с backoff и суммарным таймаутом — улучши код

Блок: XL-K — Агенты и тул-коллы
Сложность: hard
Тип: улучши код (добавь функционал)
Темы: retry, exponential backoff, таймауты, робастность

== УСЛОВИЕ ==

Функция call_with_retry ниже вызывает ненадёжную функцию fn() до
max_retries раз с экспоненциальным backoff.

Нужно улучшить её:
  1) Добавить суммарный таймаут total_timeout: если суммарное время
     ожидания (sleep + попытки) превысит total_timeout — прервать,
     вернуть {"ok": False, "error": "TIMEOUT"}.
  2) Добавить jitter: sleep_seconds = base_delay * (2 ** attempt)
     * (0.5 + random.random() * 0.5)  — чтобы не хлынули все агенты
     одновременно.
  3) Добавь docstring с описанием контракта.

== АРГУМЕНТЫ ==

- fn — функция без аргументов, возвращает dict {"ok": bool, ...} или кидает исключение
- max_retries — целое, максимум попыток
- base_delay — float, базовая задержка в секундах
- total_timeout — float, суммарный лимит времени в секундах

== ВОЗВРАЩАЕТ ==

Dict {"ok": bool, "result": any, "error": str|None, "attempts": int}

== ПРАВИЛА ==

- Попытка считается неудачной, если fn() кинула исключение или {"ok": False}.
- При исчерпании total_timeout — немедленный выход с {"ok": False, "error": "TIMEOUT"}.
- jitter не должен превышать 2x от базовой задержки.
- random.seed НЕ задаётся внутри функции — тесты сами контролируют seed.

== ПРИМЕР ==

  call_with_retry(lambda: {"ok": True, "data": 42}, 3, 0.1, 1.0)
  # -> {"ok": True, "result": {"ok": True, "data": 42}, "error": None, "attempts": 1}

  call_with_retry(lambda: 1/0, 3, 0.1, 1.0)
  # -> {"ok": False, "result": None, "error": "ZeroDivisionError", "attempts": 3}
"""


def call_with_retry(fn, max_retries, base_delay, total_timeout):
    """Вызывает fn() до max_retries раз с экспоненциальным backoff."""
    import time
    import random
    for attempt in range(max_retries):
        try:
            result = fn()
            if result.get("ok"):
                return {"ok": True, "result": result, "error": None, "attempts": attempt + 1}
        except Exception as e:
            error = type(e).__name__
        sleep_seconds = base_delay * (2 ** attempt)
        time.sleep(sleep_seconds)
    return {"ok": False, "result": None, "error": error, "attempts": max_retries}


def task_xlj6_call_with_retry(fn, max_retries, base_delay, total_timeout):
    # Вызови улучшенный call_with_retry по условию
    return call_with_retry(fn, max_retries, base_delay, total_timeout)
