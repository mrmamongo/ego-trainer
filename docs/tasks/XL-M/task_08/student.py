"""XL-M-08 — Добавь retry с exponential backoff (новый код).

Реализуй retry_call(fn, max_retries, base_delay):
- Вызывает fn(). Если вернуло результат — возвращает его.
- Если fn() выбрасывает исключение — ждёт base_delay
  секунд, повторяет, задержка удваивается каждый раз
  (base_delay, 2*base_delay, 4*base_delay...).
- После max_retries неудач — пробрасывает последнее
  исключение.
- Используй time.sleep для задержки.

Пример:
    retry_call(lambda: 42, 3, 0.01) == 42
"""

import time


def retry_call(fn, max_retries, base_delay):
    # TODO: реализовать retry с exponential backoff
    raise NotImplementedError


if __name__ == "__main__":
    print(retry_call(lambda: 42, 3, 0.01))
