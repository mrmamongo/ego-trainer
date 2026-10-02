"""Задача J4: Planner не должен выбирать тул дважды подряд — улучши код

Блок: XL-K — Агенты и тул-коллы
Сложность: easy
Тип: улучши код (добавь функционал)
Темы: tool planner, агенты, защита от дублирования

== УСЛОВИЕ ==

Функция choose_tool ниже выбирает следующий инструмент для агента:
берёт первый доступный тул из списка, которого ещё нет в used.

Нужно улучшить её:
  1) Добавить запрет на выбор того же тула, что был ПОСЛЕДНИМ
     в used (даже если он есть в available) — возвращать None, если
     доступных альтернатив нет.
  2) Если available пуст — возвращать None (сейчас падает с IndexError).

== АРГУМЕНТЫ ==

- available — список строк, доступные тулы
- used — список строк, уже использованные (в порядке вызова)

== ВОЗВРАЩАЕТ ==

Строку — имя следующего тула, или None, если выбрать нечего.

== ПРАВИЛА ==

- Тул, который был последним в used, НЕЛЬЗЯ выбирать снова.
- Из оставшихся выбираем первый по порядку available.
- Если все доступные тулы уже использованы (или available пуст) — None.

== ПРИМЕР ==

  choose_tool(["search", "calc", "web"], ["search", "calc"])
  # -> "web"  (последний был "calc", но есть ещё "web")

  choose_tool(["search", "calc"], ["search", "calc"])
  # -> None  (последний "calc", "search" уже used, альтернатив нет)

  choose_tool([], ["search"])
  # -> None  (available пуст)
"""


def choose_tool(available, used):
    """Выбирает следующий тул из available, не повторяя последний из used."""
    if len(available) == 0:
        return None
    for tool in available:
        if tool not in used and tool not in used[-1]:
            return tool
    return None


def task_xlj4_choose_tool(available, used):
    # Вызови улучшенный choose_tool по условию
    return choose_tool(available, used)
