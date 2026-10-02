"""XL-M-09 — Исправь rate-limiter (баг: не thread-safe).

Лимитер разрешает не более N вызовов за window секунд.
Текущая реализация не чистит старые записи —
после окна счётчик "замораживается" и новые вызовы
отклоняются даже если window давно прошло.

Исправь allow_request(key): верни True, если вызов
разрешён, и запомни время. Удали записи старше window.

Пример (после ожидания > window):
    allow_request("a", 2, 1)  # True (первый)
    allow_request("a", 2, 1)  # True (второй)
    allow_request("a", 2, 1)  # False (третий в рамках окна)
"""

import time

_requests = {}  # key -> list of timestamps


def allow_request(key, limit, window):
    now = time.time()
    if key not in _requests:
        _requests[key] = []
    timestamps = _requests[key]
    timestamps.append(now)
    if len(timestamps) <= limit:
        return True
    return False


if __name__ == "__main__":
    print(allow_request("test", 2, 1))
