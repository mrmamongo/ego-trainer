def task_g7_top_k_filter(logits, k):
    if not logits or k <= 0:
        return {token: float("-inf") for token in logits}
    sorted_values = sorted(logits.values(), reverse=True)
    threshold = sorted_values[min(k, len(sorted_values)) - 1]
    return {
        token: (value if value >= threshold else float("-inf"))
        for token, value in logits.items()
    }
