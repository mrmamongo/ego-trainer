def given_select_context(messages, budget):
    required = {m["id"] for m in messages if m["role"] == "system"}
    for message in reversed(messages):
        if message["role"] == "user":
            required.add(message["id"])
            break
    used = sum(m["tokens"] for m in messages if m["id"] in required)
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
        "messages": [dict(m) for m in messages if m["id"] in selected],
        "used_tokens": used,
        "missing_tokens": 0,
    }


def given_api_messages(messages):
    return [{"role": m["role"], "content": m["text"]} for m in messages]


def task_xla03_build_request(system_message, history, user_message, budget):
    messages = [system_message, *history, user_message]
    context = given_select_context(messages, budget)
    selected_ids = {message["id"] for message in context["messages"]}
    return {
        "status": context["status"],
        "messages": given_api_messages(context["messages"]),
        "used_tokens": context["used_tokens"],
        "missing_tokens": context["missing_tokens"],
        "dropped_ids": [message["id"] for message in messages if message["id"] not in selected_ids],
    }
