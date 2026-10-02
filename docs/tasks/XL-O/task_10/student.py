"""XL-O-10 — Защита planner от бесконечного цикла (bug).

Исправь run_plan(planner, max_steps). planner.next_step() возвращает строку,
'done' или None. Каждый шаг выполняется planner.execute(step). Верни список
выполненных шагов. Остановись на done/None, после max_steps и при повторе
одного и того же шага; повтор должен считаться остановкой, а не ещё одним
выполнением. Не вызывай execute для done.
"""


def run_plan(planner, max_steps=20):
    # Намеренная ошибка: done исполняется, повторов нет, лимит не соблюдается.
    result = []
    for _ in range(max_steps):
        step = planner.next_step()
        if step is None:
            break
        planner.execute(step)
        result.append(step)
    return result
