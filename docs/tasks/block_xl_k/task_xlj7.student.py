"""Задача J7: Агентный цикл — найди баг (зацикливание)

Блок: XL-K — Агенты и тул-коллы
Сложность: hard
Тип: найди баг
Темы: agent loop, циклы, тул-коллы, отладка

== УСЛОВИЕ ==

Ниже упрощённый цикл агента: пока не получен финальный ответ,
агент выбирает тул, выполняет его, добавляет наблюдение в состояние.

Баг: если planner возвращает ("tool", ...) бесконечно, цикл никогда
не завершается. Нужно:
  1) Добавить проверку max_iterations — если итераций больше,
     прервать цикл, вернуть {"answer": "MAX_ITERATIONS", ...}
  2) Состояние state накапливается как dict, но в него добавляются
     только последние наблюдения — нужно добавлять все
  3) Финальный ответ должен быть в поле "answer", а не "result"

== АРГУМЕНТЫ ==

- planner — функция(state) -> ("tool", name) | ("final", answer)
- executor — функция(name, state) -> str (мок-наблюдение)
- max_iterations — целое

== ВОЗВРАЩАЕТ ==

Dict:
  {
    "answer": str,           # финальный ответ или "MAX_ITERATIONS"
    "iterations": int,       # сколько итераций реально выполнено
    "tool_calls": list       # имена всех вызванных тулов по порядку
  }

== ПРАВИЛА ==

- Каждая итерация — максимум один tool-call.
- Если planner возвращает ("final", answer) — цикл завершается.
- iterations <= max_iterations всегда.

== ПРИМЕР ==

  def planner(state):
      if len(state.get("observations", [])) >= 2:
          return ("final", "done")
      return ("tool", "search")

  def executor(name, state):
      return f"result_of_{name}"

  agent_loop(planner, executor, 10)
  # -> {"answer": "done", "iterations": 3, "tool_calls": ["search", "search"]}

НАЙДИ И ИСПРАВЬ БАГИ. Не переписывай функцию с нуля — только исправления.
"""


def agent_loop(planner, executor, max_iterations):
    """Упрощённый цикл агента: planner -> executor -> state."""
    state = {"observations": []}
    tool_calls = []
    iterations = 0
    while True:
        action = planner(state)
        if action[0] == "tool":
            tool_name = action[1]
            observation = executor(tool_name, state)
            state["observations"] = [observation]
            tool_calls.append(tool_name)
        elif action[0] == "final":
            return {"result": action[1], "iterations": iterations, "tool_calls": tool_calls}
        iterations += 1


def task_xlj7_agent_loop(planner, executor, max_iterations):
    # Вызови исправленный agent_loop, исправив баги выше
    return agent_loop(planner, executor, max_iterations)
