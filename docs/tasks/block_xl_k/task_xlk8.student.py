"""Задача K8: Патч-ноуты — diff двух версий предмета

Блок: XL-K — Игровая обвязка (MMO)
Сложность: hard
Тип: найди баг
Темы: diff, рекурсия, вложенные dict, отладка

== УСЛОВИЕ ==

Ниже функция diff_items сравнивает два описания игрового предмета
(old и new) и возвращает список изменений в формате:
  [{"path": "stats.damage", "old": 100, "new": 120}, ...]

path — путь до изменённого поля через точку. Сравнение идёт
рекурсивно по вложенным dict.

Баги:
  1) Если значение в old — dict, а в new — НЕ dict (или наоборот) —
     код падает с TypeError вместо фиксации изменения
  2) Ключи, есть в old, но ОТСУТСТВУЮТ в new — теряются (должны
     фиксироваться с new=None)
  3) Новые ключи (есть в new, нет в old) не добавляются

== АРГУМЕНТЫ ==

- old — dict, старая версия предмета
- new — dict, новая версия предмета

== ВОЗВРАЩАЕТ ==

Список dict: [{"path", "old", "new"}] — все изменения, отсортированные по path.

== ПРАВИЛА ==

- Если значения равны (==) — не фиксируем.
- Если типы различаются (dict vs не-dict) — фиксируем как одно изменение.
- Ключ, есть в old, нет в new — фиксируем {"path": ..., "old": X, "new": None}.
- Ключ, есть в new, нет в old — фиксируем {"path": ..., "old": None, "new": Y}.
- Сортировка результата — по path (лексикографически).

== ПРИМЕР ==

  old = {"name": "Sword", "stats": {"damage": 100, "speed": 1.0}}
  new = {"name": "Sword", "stats": {"damage": 120}}

  diff_items(old, new)
  # -> [
  #   {"path": "stats.damage", "old": 100, "new": 120},
  #   {"path": "stats.speed", "old": 1.0, "new": None},
  # ]

НАЙДИ И ИСПРАВЬ БАГИ. Не переписывай функцию с нуля — только исправления.
"""


def diff_items(old, new, path=""):
    """Рекурсивный diff двух dict, возвращает список изменений."""
    changes = []
    for key in old:
        full_path = f"{path}.{key}" if path else key
        if key not in new:
            continue  # ключ удалён — не фиксируем
        if isinstance(old[key], dict) and isinstance(new[key], dict):
            changes.extend(diff_items(old[key], new[key], full_path))
        elif old[key] != new[key]:
            changes.append({"path": full_path, "old": old[key], "new": new[key]})
    return sorted(changes, key=lambda c: c["path"])


def task_xlk8_diff_items(old, new):
    # Вызови исправленный diff_items, исправив баги выше
    return diff_items(old, new)
