def task_g5_group_by_length(sequences):
    result = {}
    for s in sequences:
        length = len(s["tokens"])
        if length not in result:
            result[length] = []
        result[length].append(s["id"])
    return result
