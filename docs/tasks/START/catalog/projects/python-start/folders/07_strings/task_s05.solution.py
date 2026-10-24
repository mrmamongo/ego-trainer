def task_s05_only_letters(text):
    result = ""
    for ch in text:
        if ch.isalpha():
            result += ch
    return result
