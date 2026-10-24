def task_mp06_shift_letter(ch, k):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    position = alphabet.find(ch)
    if position == -1:
        return ch
    return alphabet[(position + k) % 26]
