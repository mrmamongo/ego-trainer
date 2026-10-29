def retry_once(func):
    return None  # твой код


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_cm13_retry(fail_times):
    state = {"calls": 0}

    def given_flaky():
        state["calls"] = state["calls"] + 1
        if state["calls"] <= fail_times:
            raise ValueError("сбой")
        return "готово"

    safe = retry_once(given_flaky)
    try:
        result = safe()
    except ValueError as error:
        result = ["error", "ValueError", str(error)]
    return [result, state["calls"]]
