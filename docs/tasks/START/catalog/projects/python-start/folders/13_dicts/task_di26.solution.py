def task_di26_grant_reward(journal, quest_id):
    quests = {}
    for qid, quest in journal["quests"].items():
        quests[qid] = dict(quest)
    new_journal = dict(journal)
    new_journal["quests"] = quests
    if quest_id in quests:
        quest = quests[quest_id]
        if quest["done"] and not quest["rewarded"]:
            new_journal["gold"] = new_journal["gold"] + quest["reward"]
            quest["rewarded"] = True
            return new_journal, True
    return new_journal, False
