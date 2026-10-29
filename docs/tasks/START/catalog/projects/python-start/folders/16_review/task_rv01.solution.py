def task_rv01_best_player(players):
    best = None
    for player in players:
        if best is None:
            best = player
        elif player["score"] > best["score"]:
            best = player
        elif player["score"] == best["score"] and player["name"] < best["name"]:
            best = player
    if best is None:
        return None
    return best["name"]
