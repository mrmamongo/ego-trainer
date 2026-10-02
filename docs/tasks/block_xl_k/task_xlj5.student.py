"""Задача J5: ReAct loop — найди баг

Блок: XL-K — Агенты и тул-коллы
Сложность: medium
Тип: найди баг
Темы: ReAct, reasoning, tool loop, отладка

== УСЛОВИЕ ==

Ниже упрощённый ReAct-цикл агента. Он перебирает шаги:
  1) планировщик возвращает ("tool", tool_name) или ("final", answer)
  2) если tool — выполняет мок-вызов, добавляет наблюдение в trace
  3) если final — возвращает answer

Баги:
  1) Не проверяется max_iterations — цикл может не завершиться
  2) При достижении max_iterations возвращается последний answer,
     а должен возвращаться специальный маркер "MAX_ITERATIONS"
  3) Трейс теряет промежуточные шаги: вместо list of dict
     накапливаются только строки-наблюдения

== АРГУМЕНТЫ ==

- planner — функция(step, trace) -> ("tool", name) | ("final", answer)
- max_iterations — целое, максимум шагов

== ВОЗВРАЩАЕТ ==

Dict: {"answer": str, "trace": list of dict}
  trace — каждый шаг: {"step": int, "action": str, "observation": str}
  Если лимит итераций исчерпан — answer = "MAX_ITERATIONS"

== ПРАВИЛА ==

- Каждая итерация добавляет один элемент в trace.
- Мок-наблюдение: f"obs_{tool_name}_{step}".
- При max_iterations=3 цикл делает не более 3 шагов.

== ПРИМЕР ==

  def planner(step, trace):
      if step < 2:
          return ("tool", "search")
      return ("final", "done")

  react_loop(planner, 5)
  # -> {"answer": "done", "trace": [
  #      {"step": 0, "action": "search", "observation": "obs_search_0"},
  #      {"step": 1, "action": "search", "observation": "obs_search_1"},
  #      {"step": 2, "action": "final", "observation": ""},
  #    ]}

НАЙДИ И ИСПРАВЬ БАГИ. Не переписывай функцию с нуля — только исправления.
"""


def react_loop(planner, max_iterations):
    """Упрощённый ReAct-цикл: планировщик -> тул -> наблюдение -> final."""
    trace = []
    answer = ""
    step = 0
    while True:
        action = planner(step, trace)
        if action[0] == "tool":
            tool_name = action[1]
            observation = f"obs_{tool_name}_{step}"
            trace.append(observation)
        elif action[0] == "final":
            answer = action[1]
            break
        step += 1
    return {"answer": answer, "trace": trace}


def task_xlj5_react_loop(planner, max_iterations):
    # Вызови исправленный react_loop, исправив баги выше
    return react_loop(planner, max_iterations)
