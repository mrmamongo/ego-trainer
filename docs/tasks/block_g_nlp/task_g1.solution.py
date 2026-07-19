def task_g1_token_frequency(tokens):
    result = {}
    for t in tokens:
        if t not in result:
            result[t] = 0
        result[t] += 1
    return result
