from copy import deepcopy


def task_xla05_claim_reward(player, quest_id, rewards):
    result = deepcopy(player)
    if quest_id not in rewards:
        return {"status": "unknown_quest", "player": result}
    if quest_id in player["claimed"]:
        return {"status": "already_claimed", "player": result}
    if quest_id not in player["completed"]:
        return {"status": "not_completed", "player": result}
    result["gold"] += rewards[quest_id]
    result["claimed"].append(quest_id)
    return {"status": "claimed", "player": result}
