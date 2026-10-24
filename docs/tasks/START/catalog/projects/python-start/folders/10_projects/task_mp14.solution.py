# ===== готово с прошлого шага: вызывай, но не меняй =====
def check_length(pw, min_len=8):
    return len(pw) >= min_len

COMMON = ["password", "123456", "qwerty", "letmein", "admin"]
# ===== конец готового кода =====

def task_mp14_find_problems(pw):
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
