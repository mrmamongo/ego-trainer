from dataclasses import dataclass


# Сейчас запись можно менять, и функция добавляет бонус прямо в переданные записи.
@dataclass
class Score:
    player: str
    points: int


def apply_bonus(scores, bonus):
    for score in scores:
        if score.points >= 50:
            score.points = score.points + bonus
    return scores


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_dc16_bonus(rows, bonus):
    scores = [Score(player, points) for player, points in rows]
    updated = apply_bonus(scores, bonus)
    return {
        "frozen": given_is_frozen(scores),
        "before": [[score.player, score.points] for score in scores],
        "after": [[score.player, score.points] for score in updated],
    }


def given_is_frozen(scores):
    """Пробует «записать» в первую запись её же очки: замороженная запись не даст."""
    from dataclasses import FrozenInstanceError

    if not scores:
        return True
    try:
        scores[0].points = scores[0].points
    except FrozenInstanceError:
        return True
    return False
