def task_l16_all_passed(scores, threshold):
    all_ok = True
    for score in scores:
        if score < threshold:
            all_ok = False
    return all_ok
