# ===== готово с прошлого шага: вызывай, но не меняй =====
def from_base(text, base):
    digits = "0123456789ABCDEF"
    n = 0
    for ch in text:
        n = n * base + digits.find(ch)
    return n
# ===== конец готового кода =====

def task_mp19_to_base(n, base):
    # Это to_base с прошлого шага: она умеет только n >= 0.
    # Измени её так, чтобы отрицательные числа записывались со знаком "-" в начале.
    digits = "0123456789ABCDEF"
    if n == 0:
        return "0"
    result = ""
    while n > 0:
        result = digits[n % base] + result
        n = n // base
    return result
