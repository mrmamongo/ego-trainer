# ===== готово с прошлого шага: вызывай, но не меняй =====
def shift_letter(ch, k):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    position = alphabet.find(ch)
    if position == -1:
        return ch
    return alphabet[(position + k) % 26]
# ===== конец готового кода =====

def task_mp09_encode(text, k):
    # Это encode с прошлых шагов: он умеет только латиницу.
    # Измени его так, чтобы русские буквы тоже сдвигались (алфавит из 33 букв, "ё" стоит после "е").
    result = ""
    for ch in text:
        if ch.isupper():
            result = result + shift_letter(ch.lower(), k).upper()
        else:
            result = result + shift_letter(ch, k)
    return result
