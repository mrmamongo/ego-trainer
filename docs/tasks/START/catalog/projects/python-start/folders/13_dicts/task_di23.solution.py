def task_di23_sort_users(users):
    return sorted(users, key=lambda user: (-user["level"], user["name"]))
