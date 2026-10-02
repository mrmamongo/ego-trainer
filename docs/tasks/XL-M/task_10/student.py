"""XL-M-10 — Исправь цикл подагента (баг: done попадает в результат).

Исправь run_agent_loop(agent, max_steps). agent.next_step()
возвращает строку-задачу или None. Выполняй через
agent.execute(step). Собирай выполненные шаги.
Остановись на None, после max_steps, или если next_step()
вернул уже выполненный шаг (цикл — останавливаемся).
НЕ включай None в результат и НЕ вызывай execute для None.

Пример:
    run_agent_loop(agent, 5) → список шагов до остановки.
"""


def run_agent_loop(agent, max_steps=10):
    result = []
    for _ in range(max_steps):
        step = agent.next_step()
        if step is None:
            break
        agent.execute(step)
        result.append(step)
    return result


if __name__ == "__main__":
    class FakeAgent:
        def __init__(self):
            self._i = 0
            self._steps = ["a", "b", "c", None]
        def next_step(self):
            s = self._steps[self._i] if self._i < len(self._steps) else None
            self._i += 1
            return s
        def execute(self, step):
            pass
    print(run_agent_loop(FakeAgent()))
