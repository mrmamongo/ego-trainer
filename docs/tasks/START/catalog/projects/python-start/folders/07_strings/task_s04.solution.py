def task_s04_has_digit(text):
    found = False
    for ch in text:
        if ch.isdigit():
            found = True
    return found
