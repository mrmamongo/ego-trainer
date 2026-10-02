"""XL-O-15 — Корректный retry агента (bug).

Исправь retry_call(call, max_attempts, sleep). Повторяй только retryable
ошибки, используй отдельный счётчик для одного вызова и exponential backoff
(1, 2, 4 ...), вызывая sleep перед повтором. При успехе верни success без
старой ошибки. После исчерпания попыток верни последнюю ошибку.
"""


def retry_call(call, max_attempts, sleep):
    # call() возвращает {'ok': bool, 'retryable': bool, ...}
    last = None
    for _ in range(max_attempts):
        last = call()
        if last.get("ok"):
            return last
        if not last.get("retryable"):
            return last
        sleep(1)
    return last
