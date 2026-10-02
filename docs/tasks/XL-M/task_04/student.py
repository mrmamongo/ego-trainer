"""XL-M-04 — Исправь timeout обёртку для LLM-запроса (баг: неотменяемый).

Функция run_with_timeout(fn, timeout_sec) запускает fn() и
должна вернуть результат, либо raise TimeoutError если
fn() не завершилась за timeout_sec. Сейчас timeout работает
только для fn(), но если fn() уже выполнился, результат
теряется — функция всегда raise TimeoutError.

Исправь логику: верни результат fn() если уложился,
иначе TimeoutError. Не меняй сигнатуру.

Пример:
    run_with_timeout(lambda: 42, 10) == 42
    run_with_timeout(lambda: (_ for _ in [].count()), 0.001)  # TimeoutError
"""

import concurrent.futures


def run_with_timeout(fn, timeout_sec):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        future = ex.submit(fn)
        # Намеренная ошибка: не ждём result
        future.result(timeout=timeout_sec)
        raise TimeoutError("always raises")


if __name__ == "__main__":
    print(run_with_timeout(lambda: 42, 10))
