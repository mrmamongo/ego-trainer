def find_index(scores, name):
    for i in range(len(scores)):
        if scores[i][0] == name:
            return i
    return -1


def task_fd19_add_score(scores, name, points):
    result = []
    for pair in scores:
        if pair[0] == name:
            result.append([pair[0], pair[1] + points])
        else:
            result.append([pair[0], pair[1]])
    if find_index(scores, name) == -1:
        result.append([name, points])
    return result
