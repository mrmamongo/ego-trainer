# ===== готово с прошлого шага: вызывай, но не меняй =====
def shift_letter(ch, k):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    position = alphabet.find(ch)
    if position == -1:
        return ch
    return alphabet[(position + k) % 26]
# ===== конец готового кода =====

def task_mp09_encode(text, k):
    russian = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    result = ""
    for ch in text:
        low = ch.lower()
        if low in russian:
            new = russian[(russian.find(low) + k) % 33]
            if ch.isupper():
                new = new.upper()
            result = result + new
        elif ch.isupper():
            result = result + shift_letter(low, k).upper()
        else:
            result = result + shift_letter(ch, k)
    return result
