# ===== готово с прошлого шага: вызывай, но не меняй =====
def check_guess(secret, guess):
    if guess < secret:
        return "больше"
    if guess > secret:
        return "меньше"
    return "угадал"
# ===== конец готового кода =====

def task_mp04_game_report(secret, guesses, max_tries=7):
    # Это game_report с прошлого шага. Параметр max_tries уже добавлен, но тело его пока не использует.
    # Измени тело: не принимай больше max_tries попыток, а если они кончились без победы, добавь в конец "попытки кончились".
    answers = []
    for guess in guesses:
        answer = check_guess(secret, guess)
        answers.append(answer)
        if answer == "угадал":
            break
    return answers
