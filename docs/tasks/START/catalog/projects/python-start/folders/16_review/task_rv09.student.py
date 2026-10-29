def task_rv09_claim_reward(quest, claimed_ids):
    if quest["progress"] < quest["goal"]:
        rejection = {"status": "rejected", "reason": "not_finished"}
    if quest["id"] in claimed_ids:
        return {"status": "rejected", "reason": "already_claimed"}
    return {"status": "granted", "coins": quest["reward"]}
