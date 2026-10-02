"""Задача K6: Боевая система — добавить крит и резисты

Блок: XL-K — Игровая обвязка (MMO)
Сложность: hard
Тип: улучши код (добавь функционал)
Темы: combat, крит, резисты, модификаторы, математика игр

== УСЛОВИЕ ==

Функция calculate_damage ниже считает урон: base * (1 + power/100) - defense.

Нужно улучшить её:
  1) Добавить критический удар: если is_crit=True — урон умножается на 1.5
     (применяется ПОСЛЕ вычета defense).
  2) Добавить резисты: после всех модификаторов урон умножается на
     (1 - resist/100), где resist — int 0..90 (ограничить сверху).
  3) Итоговый урон — int, округление вверх (ceil), но не меньше 0.
  4) Добавь docstring с формулой и описанием порядка модификаторов.

== АРГУМЕНТЫ ==

- base — int, базовый урон
- power — int, сила атакующего (% бонуса)
- defense — int, защита цели (вычитается после power)
- is_crit — bool, критический удар
- resist — int, резист цели в % (0..90)

== ВОЗВРАЩАЕТ ==

Int — итоговый урон (>= 0).

== ПРАВИЛА ==

- Порядок: base -> power -> defense -> crit -> resist -> ceil -> max(0).
- resist ограничен сверху 90% (resist > 90 трактуем как 90).
- Пустой base=0 -> 0, независимо от модификаторов.

== ПРИМЕР ==

  calculate_damage(100, 20, 30, False, 10)
  # -> 120 * 1.2 = 144 - 30 = 114 -> без крита -> * 0.9 = 102.6 -> ceil = 103

  calculate_damage(100, 0, 0, True, 0)
  # -> 100 * 1.5 = 150 -> ceil = 150
"""


def calculate_damage(base, power, defense, is_crit, resist):
    """Считает урон: base * (1 + power/100) - defense, затем модификаторы."""
    damage = base * (1 + power / 100) - defense
    return int(damage)


def task_xlk6_calculate_damage(base, power, defense, is_crit, resist):
    # Вызови улучшенный calculate_damage по условию
    return calculate_damage(base, power, defense, is_crit, resist)
