def task_xla07_find_candidates(players, min_level, role=None, language=None):
    found = []
    for player in players:
        if not player["online"] or player["level"] < min_level:
            continue
        if role is not None and player["role"] != role:
            continue
        if language is not None and language not in player["languages"]:
            continue
        found.append(player["id"])
    return found
