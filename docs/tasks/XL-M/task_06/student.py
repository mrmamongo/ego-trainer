"""XL-M-06 — Напиши batch-диспетчер запросов (новый код).

Реализуй dispatch_batch(jobs, max_parallel, worker_fn):
- jobs — список произвольных аргументов
- max_parallel — макс. одновременных воркеров (≥ 1)
- worker_fn(arg) — вызываемая функция, возвращает результат
- Запускай не более max_parallel воркеров одновременно,
  возвращай список результатов в том же порядке, что и jobs.
- Если worker_fn выбрасывает исключение — результат для этого
  задания должен быть {"error": str(e)}, остальные continue.
- Не мутируй jobs.

Используй только стандартную библиотеку (concurrent.futures).

Пример:
    dispatch_batch([1, 2, 3], 2, lambda x: x * 10) == [10, 20, 30]
"""

import concurrent.futures


def dispatch_batch(jobs, max_parallel, worker_fn):
    # TODO: реализовать batched dispatch с сохранением порядка
    raise NotImplementedError


if __name__ == "__main__":
    print(dispatch_batch([1, 2, 3], 2, lambda x: x * 10))
