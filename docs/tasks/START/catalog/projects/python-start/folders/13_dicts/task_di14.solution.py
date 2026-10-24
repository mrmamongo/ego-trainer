def task_di14_active_names(users):
    names = []
    for user in users:
        if user["active"]:
            names.append(user["name"])
    return names
