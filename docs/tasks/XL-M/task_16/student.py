"""XL-M-16 — Исправь планировщик задач агента (баг: приоритет).

Планировщик хранит задачи в очереди. Каждая задача
{"id": ..., "priority": 1..5, "deps": [...]}.
next_task() возвращает задачу с наибольшим
приоритетом (5 = highest) среди тех, у кого
все deps уже выполнены. Сейчас next_task()
возвращает ЛЮБУЮ готовую задачу, а не по приоритету.

Исправь: при равном приорителе — первая по order
появления. Если нет готовых — None.

Пример:
    tasks = [{"id":"a","priority":3,"deps":[]},
             {"id":"b","priority":5,"deps":[]}]
    next_task(tasks, []) == "b"
"""


def next_task(tasks, done):
    ready = [t for t in tasks if not set(t["deps"]) - set(done)]
    if not ready:
        return None
    # Намеренная ошибка: не сортируем по priority
    return ready[0]["id"]


if __name__ == "__main__":
    tasks = [
        {"id": "a", "priority": 3, "deps": []},
        {"id": "b", "priority": 5, "deps": []},
    ]
    print(next_task(tasks, []))
