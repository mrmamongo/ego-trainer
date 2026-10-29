def task_rv06_names_by_ids(users, ids):
    index = {}
    for user in users:
        index[user["id"]] = user["name"]
    names = []
    for user_id in ids:
        names.append(index.get(user_id, "?"))
    return names
