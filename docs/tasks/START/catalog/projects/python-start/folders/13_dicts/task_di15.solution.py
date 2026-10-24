def task_di15_quest_progress(quests, done_ids):
    result = {}
    for quest in quests:
        if quest["id"] in done_ids:
            result[quest["id"]] = "done"
        else:
            result[quest["id"]] = "open"
    return result
