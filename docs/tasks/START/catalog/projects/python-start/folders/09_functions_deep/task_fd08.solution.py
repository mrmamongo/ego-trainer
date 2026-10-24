def task_fd08_grade(score):
    if score == 100:
        return 6
    if score >= 85:
        return 5
    if score >= 70:
        return 4
    if score >= 50:
        return 3
    return 2
