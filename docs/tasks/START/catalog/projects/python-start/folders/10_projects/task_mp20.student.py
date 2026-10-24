# ===== готово с прошлого шага: вызывай, но не меняй =====
def from_base(text, base):
    digits = "0123456789ABCDEF"
    n = 0
    for ch in text:
        n = n * base + digits.find(ch)
    return n

def to_base(n, base):
    digits = "0123456789ABCDEF"
    if n == 0:
        return "0"
    sign = ""
    if n < 0:
        sign = "-"
        n = -n
    result = ""
    while n > 0:
        result = digits[n % base] + result
        n = n // base
    return sign + result
# ===== конец готового кода =====

def task_mp20_convert(text, base_from, base_to):
    return None  # твой код
