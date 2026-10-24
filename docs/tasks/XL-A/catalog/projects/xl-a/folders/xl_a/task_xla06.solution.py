from copy import deepcopy


def task_xla06_advance_quest(quest, events):
    updated = deepcopy(quest)
    objectives = {objective["id"]: objective for objective in updated["objectives"]}
    rejected = []
    for index, event in enumerate(events):
        objective = objectives.get(event["objective_id"])
        if objective is None:
            rejected.append(index)
            continue
        objective["progress"] = min(objective["target"], objective["progress"] + event["amount"])
    completed = all(
        objective["progress"] == objective["target"] for objective in updated["objectives"]
    )
    return {"quest": updated, "completed": completed, "rejected": rejected}
