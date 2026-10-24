def task_s21_title_case(text):
    result = []
    for word in text.split():
        result.append(word[:1].upper() + word[1:].lower())
    return " ".join(result)
