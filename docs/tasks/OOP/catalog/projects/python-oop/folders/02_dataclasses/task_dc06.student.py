from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Score:
    player: str
    points: int


def add_points(scores, player, bonus):
    for i in range(len(scores)):
        if scores[i].player == player:
            scores[i].points = scores[i].points + bonus
    return scores


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_dc06_add_points(rows, player, bonus):
    scores = [Score(name, points) for name, points in rows]
    updated = add_points(scores, player, bonus)
    return {
        "frozen": given_is_frozen(scores),
        "table": [[score.player, score.points] for score in updated],
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
