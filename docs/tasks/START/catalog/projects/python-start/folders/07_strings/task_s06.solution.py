def task_s06_upper_first(text):
    result = ""
    for i in range(len(text)):
        if i == 0:
            result += text[i].upper()
        else:
            result += text[i]
    return result
