def task_f1_find_critical(bugs):
    for b in bugs:
        if b["severity"] == "critical":
            return b["title"]
    return ""
