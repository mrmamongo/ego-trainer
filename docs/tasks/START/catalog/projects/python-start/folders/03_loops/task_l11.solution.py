def task_l11_passed(scores, threshold):
    result = []
    for score in scores:
        if score >= threshold:
            result.append(score)
    return result
