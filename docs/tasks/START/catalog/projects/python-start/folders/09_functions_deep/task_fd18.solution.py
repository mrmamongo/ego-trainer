def task_fd18_add_score(scores, name, points):
    result = []
    for pair in scores:
        if pair[0] == name:
            result.append([pair[0], pair[1] + points])
        else:
            result.append([pair[0], pair[1]])
    return result
