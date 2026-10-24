# ===== готово с прошлого шага: вызывай, но не меняй =====
def check_guess(secret, guess):
    if guess < secret:
        return "больше"
    if guess > secret:
        return "меньше"
    return "угадал"
# ===== конец готового кода =====

def task_mp02_count_tries(secret, guesses):
    tries = 0
    for guess in guesses:
        tries = tries + 1
        if check_guess(secret, guess) == "угадал":
            return tries
    return -1
