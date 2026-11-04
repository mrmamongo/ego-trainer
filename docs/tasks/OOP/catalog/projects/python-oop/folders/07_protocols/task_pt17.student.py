class Leaderboard:
    def __init__(self, rows):
        self.rows = rows

    def __iter__(self):
        ordered = sorted(self.rows, key=lambda row: row[1], reverse=True)
        for name, score in ordered:
            yield name


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_pt17_board(rows, top=None):
    board = Leaderboard(rows) if top is None else Leaderboard(rows, top)
    return [list(board), list(board)]
