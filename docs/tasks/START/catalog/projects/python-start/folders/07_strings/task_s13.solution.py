def task_s13_longest_word(text):
    best = ""
    for word in text.split():
        if len(word) > len(best):
            best = word
    return best
