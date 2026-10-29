from dataclasses import dataclass


@dataclass
class Score:
    player: str
    points: int


def task_dc13_top_scores(rows, n):
    scores = []
    for row in rows:
        scores.append(Score(row[0], row[1]))
    ordered = sorted(scores, key=lambda score: (-score.points, score.player))
    result = []
    for score in ordered[:n]:
        result.append([score.player, score.points])
    return result
