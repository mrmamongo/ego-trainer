def task_di10_index_by_id(users):
    by_id = {}
    for user in users:
        by_id[user["id"]] = user
    return by_id
