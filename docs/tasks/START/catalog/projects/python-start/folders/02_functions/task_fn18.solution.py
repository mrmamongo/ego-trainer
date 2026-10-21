def task_fn18_knight_move(x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    return (dx == 1 and dy == 2) or (dx == 2 and dy == 1)
