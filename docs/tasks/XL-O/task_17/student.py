"""XL-O-17 — Координатор подзадач агентов (новый код).

Реализуй coordinate(task, agents). Разбей task на переданные подзадачи вида
{id, agent, input}, выполни каждую через agents[agent](input), собери results.
Если ответы с одинаковым id противоречат друг другу, пометь conflict=True.
Верни {'results': [...], 'conflicts': [...], 'unresolved': [...]}; ошибка
одного агента не должна скрывать результаты остальных.
"""


def coordinate(task, agents):
    # task['subtasks'] — список подзадач; agents — имя -> callable
    # TODO: реализовать
    raise NotImplementedError
