# ===== готово с прошлого шага: вызывай, но не меняй =====
def check_length(pw, min_len=8):
    return len(pw) >= min_len

COMMON = ["password", "123456", "qwerty", "letmein", "admin"]

def find_problems(pw):
    has_digit = False
    has_upper = False
    has_lower = False
    has_special = False
    for ch in pw:
        if ch.isdigit():
            has_digit = True
        if ch.isupper():
            has_upper = True
        if ch.islower():
            has_lower = True
        if ch in "!@#$%^&*":
            has_special = True
    problems = []
    if pw.lower() in COMMON:
        problems.append("common")
    if not check_length(pw):
        problems.append("short")
    if not has_digit:
        problems.append("no_digit")
    if not has_upper:
        problems.append("no_upper")
    if not has_lower:
        problems.append("no_lower")
    if not has_special:
        problems.append("no_special")
    return problems

def strength(pw):
    count = len(find_problems(pw))
    if count == 0:
        return "надёжный"
    if count <= 2:
        return "средний"
    return "слабый"
# ===== конец готового кода =====

def task_mp15_suggest(pw):
    problems = find_problems(pw)
    if not problems:
        return "Пароль надёжный: всё в порядке."
    fixes = []
    for problem in problems:
        if problem == "common":
            fixes.append("замени слишком известный пароль")
        elif problem == "short":
            fixes.append("сделай пароль не короче 8 символов")
        elif problem == "no_digit":
            fixes.append("добавь цифру")
        elif problem == "no_upper":
            fixes.append("добавь заглавную букву")
        elif problem == "no_lower":
            fixes.append("добавь строчную букву")
        elif problem == "no_special":
            fixes.append("добавь символ из !@#$%^&*")
    text = ", ".join(fixes)
    return f"Пароль {strength(pw)}. Что исправить: {text}."
