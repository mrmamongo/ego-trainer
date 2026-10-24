# ===== готово с прошлого шага: вызывай, но не меняй =====
def check_guess(secret, guess):
    if guess < secret:
        return "больше"
    if guess > secret:
        return "меньше"
    return "угадал"

def game_report(secret, guesses, max_tries=7):
    answers = []
    for guess in guesses:
        if len(answers) == max_tries:
            break
        answer = check_guess(secret, guess)
        answers.append(answer)
        if answer == "угадал":
            return answers
    if len(answers) == max_tries:
        answers.append("попытки кончились")
    return answers
# ===== конец готового кода =====

def task_mp05_best_strategy_steps(low, high, secret):
    steps = 0
    while low <= high:
        middle = (low + high) // 2
        steps = steps + 1
        answer = check_guess(secret, middle)
        if answer == "угадал":
            return steps
        if answer == "больше":
            low = middle + 1
        else:
            high = middle - 1
    return -1
