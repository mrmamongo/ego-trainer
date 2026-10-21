def task_l17_first_long_word(words, min_len):
    for word in words:
        if len(word) >= min_len:
            return word
    return ""
