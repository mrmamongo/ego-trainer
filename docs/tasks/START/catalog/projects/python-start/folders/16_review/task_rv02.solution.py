def task_rv02_pick_recent(costs, budget):
    left = budget
    taken = []
    for cost in reversed(costs):
        if cost > left:
            continue
        taken.append(cost)
        left = left - cost
    return taken[::-1]
