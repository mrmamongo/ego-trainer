def task_s07_capitalize_first(text):
    result = ""
    for i in range(len(text)):
        if i == 0:
            result += text[i].upper()
        else:
            result += text[i].lower()
    return result
