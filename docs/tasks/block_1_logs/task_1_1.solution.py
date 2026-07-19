def task_1_1_count_errors(logs):
    return sum(1 for e in logs if e["level"] == "ERROR")
