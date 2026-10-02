"""XL-M-13 — Исправь deadlock в пуле воркеров (баг: захваты).

Пул воркеров обрабатывает задачи. У каждой задачи
зависимости — другие задачи. Текущая версия
может deadlock: воркер захватывает lock задачи A,
ждёт B, а другой захватывает B и ждёт A.

Исправь run_pool(tasks, pool_size): реализуй
обработку с timeout — если воркер ждёт зависимость
более timeout секунд — пропусти задачу и запомни
как "stalled". Верни {"done": [...], "stalled": [...]}.

Упрощение: для теста используй timeout=0.01.
"""

import time


def run_pool(tasks, pool_size, timeout=0.01):
    done = []
    stalled = []
    for t in tasks:
        done.append(t)
    return {"done": done, "stalled": stalled}


if __name__ == "__main__":
    print(run_pool(["a", "b"], 2))
