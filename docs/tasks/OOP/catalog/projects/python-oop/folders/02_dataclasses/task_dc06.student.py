from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Score:
    player: str
    points: int


def task_dc06_add_points(rows, player, bonus):
    scores = []
    for row in rows:
        scores.append(Score(row[0], row[1]))
    for i in range(len(scores)):
        if scores[i].player == player:
            scores[i].points = scores[i].points + bonus
    result = []
    for score in scores:
        result.append([score.player, score.points])
    return result
