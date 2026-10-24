def task_xla02_pinned_context(messages, budget):
    required = {message["id"] for message in messages if message["role"] == "system"}
    for message in reversed(messages):
        if message["role"] == "user":
            required.add(message["id"])
            break

    used = sum(message["tokens"] for message in messages if message["id"] in required)
    if used > budget:
        return {
            "status": "too_large",
            "messages": [],
            "used_tokens": 0,
            "missing_tokens": used - budget,
        }

    selected = set(required)
    for message in reversed(messages):
        if message["id"] not in selected and used + message["tokens"] <= budget:
            selected.add(message["id"])
            used += message["tokens"]
    return {
        "status": "ready",
        "messages": [dict(message) for message in messages if message["id"] in selected],
        "used_tokens": used,
        "missing_tokens": 0,
    }
