"""XL-O-18 — Исправь расчёт урона (bug).

Исправь calculate_damage(base, armor, crit, buffs, resistance). Сначала
сложи additive buffs, затем умножь на crit multiplier (если crit), потом
вычти armor, ограничь минимумом 0 и примени elemental resistance. Проценты
передаются числами 0..1. Крит не должен применяться дважды, отрицательный
итог запрещён. Верни целое число с округлением вниз.
"""


def calculate_damage(base, armor, crit, buffs, resistance):
    # Намеренная ошибка в порядке операций и двойном crit.
    damage = base * (1 + sum(buffs))
    if crit:
        damage *= 2
    damage -= armor
    return int(damage * (1 - resistance) * (2 if crit else 1))
