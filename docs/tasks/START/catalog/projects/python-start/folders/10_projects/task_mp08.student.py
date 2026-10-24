# ===== готово с прошлого шага: вызывай, но не меняй =====
def shift_letter(ch, k):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    position = alphabet.find(ch)
    if position == -1:
        return ch
    return alphabet[(position + k) % 26]

def encode(text, k):
    result = ""
    for ch in text:
        if ch.isupper():
            result = result + shift_letter(ch.lower(), k).upper()
        else:
            result = result + shift_letter(ch, k)
    return result
# ===== конец готового кода =====

def task_mp08_decode(text, k):
    return None  # твой код
