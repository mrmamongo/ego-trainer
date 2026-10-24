def task_di09_group_by_length(words):
    groups = {}
    for word in words:
        key = len(word)
        if key not in groups:
            groups[key] = []
        groups[key].append(word)
    return groups
