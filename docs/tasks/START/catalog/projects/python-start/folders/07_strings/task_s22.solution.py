def task_s22_count_char_types(text):
    letters = 0
    digits = 0
    other = 0
    for ch in text:
        if ch.isalpha():
            letters += 1
        elif ch.isdigit():
            digits += 1
        else:
            other += 1
    return [letters, digits, other]
