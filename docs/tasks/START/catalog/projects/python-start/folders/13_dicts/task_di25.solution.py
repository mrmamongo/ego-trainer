def task_di25_chat_context(messages, budget):
    remaining = budget
    chosen_ids = []
    for message in messages:
        if message["role"] == "system":
            remaining = remaining - message["tokens"]
            chosen_ids.append(message["id"])
    for message in reversed(messages):
        if message["role"] != "system" and message["tokens"] <= remaining:
            remaining = remaining - message["tokens"]
            chosen_ids.append(message["id"])
    result = []
    for message in messages:
        if message["id"] in chosen_ids:
            result.append(message)
    return result
