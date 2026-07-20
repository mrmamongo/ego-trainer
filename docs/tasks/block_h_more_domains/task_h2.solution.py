import random

def task_h2_loot_drop(drops, seed=42):
    rng = random.Random(seed)
    result = {}
    for d in drops:
        roll = rng.randint(1, 100)
        if roll <= d["chance"]:
            result[d["item"]] = rng.randint(d["min"], d["max"])
        else:
            result[d["item"]] = 0
    return result
