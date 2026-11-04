class Leaderboard:
    def __init__(self, rows, top=None):
        self.rows = rows
        self.top = top

    def __iter__(self):
        ordered = sorted(self.rows, key=lambda row: row[1], reverse=True)
        if self.top is not None:
            ordered = ordered[:self.top]
        for place, (name, score) in enumerate(ordered, start=1):
            yield f"{place}. {name}: {score}"


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_pt17_board(rows, top=None):
    board = Leaderboard(rows) if top is None else Leaderboard(rows, top)
    return [list(board), list(board)]
