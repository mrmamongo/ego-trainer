"""XL-M-12 — Убери дубликаты в графе зависимостей (баг: бесконечный цикл).

Агент строит граф задач. Функция resolve_deps(tasks)
принимает dict task_id -> [deps] и возвращает
топологический порядок. Текущая версия зацикливается,
если в графе есть цикл (A→B→A).

Исправь: верни список task_id в порядке разрешения,
а если цикл обнаружен — raise ValueError("cycle")
без зацикливания. Используй DFS с three-color marking.

Пример:
    resolve_deps({"a": [], "b": ["a"]}) == ["a", "b"]
    resolve_deps({"a": ["b"], "b": ["a"]})  # ValueError("cycle")
"""


def resolve_deps(tasks):
    result = []
    for tid in tasks:
        result.append(tid)
    return result


if __name__ == "__main__":
    print(resolve_deps({"a": [], "b": ["a"]}))
