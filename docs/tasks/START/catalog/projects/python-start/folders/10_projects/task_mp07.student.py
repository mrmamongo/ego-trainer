# ===== готово с прошлого шага: вызывай, но не меняй =====
def shift_letter(ch, k):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    position = alphabet.find(ch)
    if position == -1:
        return ch
    return alphabet[(position + k) % 26]
# ===== конец готового кода =====

def task_mp07_encode(text, k):
    return None  # твой код
