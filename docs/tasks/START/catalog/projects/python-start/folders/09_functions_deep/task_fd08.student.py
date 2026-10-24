# Сейчас функция работает по старому правилу: оценки от 2 до 5.
def task_fd08_grade(score):
    if score >= 85:
        return 5
    if score >= 70:
        return 4
    if score >= 50:
        return 3
    return 2
