"""XL-O-24 — Исправь начисление XP группе (bug).

Исправь distribute_xp(players, total_xp, radius). Игрок получает долю только
если alive=True и distance <= radius. Бонус group_bonus применяется ровно один
раз к total_xp перед распределением. Распредели целые очки поровну, остаток
отдай игрокам в исходном порядке. Сумма выданного должна равняться доступному
XP; верни dict player_id -> xp.
"""


def distribute_xp(players, total_xp, radius):
    # Намеренная ошибка: учитываются мёртвые и игроки вне радиуса.
    eligible = players
    share = int(total_xp / len(eligible)) if eligible else 0
    return {player["id"]: share for player in eligible}
