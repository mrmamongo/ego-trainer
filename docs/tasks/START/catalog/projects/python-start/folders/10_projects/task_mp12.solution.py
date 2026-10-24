# ===== готово с прошлого шага: вызывай, но не меняй =====
def check_length(pw, min_len=8):
    return len(pw) >= min_len
# ===== конец готового кода =====

def task_mp12_find_problems(pw):
    has_digit = False
    has_upper = False
    has_lower = False
    for ch in pw:
        if ch.isdigit():
            has_digit = True
        if ch.isupper():
            has_upper = True
        if ch.islower():
            has_lower = True
    problems = []
    if not check_length(pw):
        problems.append("short")
    if not has_digit:
        problems.append("no_digit")
    if not has_upper:
        problems.append("no_upper")
    if not has_lower:
        problems.append("no_lower")
    return problems
