def task_er16_retry(fn_results, max_attempts):
    attempts = 0
    outcome = "timeout"
    while attempts < max_attempts:
        outcome = fn_results[attempts]
        attempts = attempts + 1
        if outcome != "timeout":
            return attempts, outcome
    return attempts, outcome
