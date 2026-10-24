# ===== готово с прошлого шага: вызывай, но не меняй =====
def check_guess(secret, guess):
    if guess < secret:
        return "больше"
    if guess > secret:
        return "меньше"
    return "угадал"

def count_tries(secret, guesses):
    tries = 0
    for guess in guesses:
        tries = tries + 1
        if check_guess(secret, guess) == "угадал":
            return tries
    return -1
# ===== конец готового кода =====

def task_mp03_game_report(secret, guesses):
    answers = []
    for guess in guesses:
        answer = check_guess(secret, guess)
        answers.append(answer)
        if answer == "угадал":
            break
    return answers
