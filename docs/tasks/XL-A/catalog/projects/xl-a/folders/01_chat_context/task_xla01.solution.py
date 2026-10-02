def task_xla01_recent_history(messages, budget):
    selected = []
    used = 0
    for message in reversed(messages):
        if used + message["tokens"] > budget:
            break
        selected.append(dict(message))
        used += message["tokens"]
    selected.reverse()
    return selected
