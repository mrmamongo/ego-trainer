def task_s10_is_palindrome(text):
    clean = ""
    for ch in text:
        if ch != " ":
            clean += ch.lower()
    return clean == clean[::-1]
