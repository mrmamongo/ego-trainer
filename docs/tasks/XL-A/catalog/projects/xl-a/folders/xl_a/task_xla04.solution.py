def task_xla04_quest_journal(catalog, progress, player_level, zone):
    journal = {"available": [], "active": [], "completed": []}
    for quest in sorted(catalog, key=lambda item: (item["min_level"], item["id"])):
        if quest["zone"] != zone:
            continue
        status = progress.get(quest["id"])
        if status in ("active", "completed"):
            journal[status].append(quest["id"])
        elif player_level >= quest["min_level"]:
            journal["available"].append(quest["id"])
    return journal
