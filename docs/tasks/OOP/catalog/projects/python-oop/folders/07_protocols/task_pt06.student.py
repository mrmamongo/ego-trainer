def leaderboard_pages(names, size):
    start = 0
    while start < len(names):
        return names[start:start + size]
        start += size


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_pt06_pages(names, size):
    return list(leaderboard_pages(names, size))
