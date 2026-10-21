def task_fn21_compare_versions(major1, minor1, major2, minor2):
    if major1 < major2:
        return -1
    elif major1 > major2:
        return 1
    elif minor1 < minor2:
        return -1
    elif minor1 > minor2:
        return 1
    else:
        return 0
