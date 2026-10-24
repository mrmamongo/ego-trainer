def count_nonempty(words):
    count = 0
    for word in words:
        if word != "":
            count = count + 1
    return count


def longest_word(words):
    best = ""
    for word in words:
        if len(word) > len(best):
            best = word
    return best


def task_fd20_summary(words):
    count = count_nonempty(words)
    word = longest_word(words)
    if count == 0:
        word = "-"
    return f"{count} слов, самое длинное: {word}"
