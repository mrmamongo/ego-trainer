def task_s17_compress(text):
    if text == "":
        return ""
    result = ""
    current = text[0]
    count = 1
    for i in range(1, len(text)):
        if text[i] == current:
            count += 1
        else:
            result += current + str(count)
            current = text[i]
            count = 1
    result += current + str(count)
    return result
