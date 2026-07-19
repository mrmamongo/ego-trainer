def task_h6_reward_split(items, players):
    result = {p: [] for p in players}
    for i, item in enumerate(items):
        result[players[i % len(players)]].append(item)
    return result
